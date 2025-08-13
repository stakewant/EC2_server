from flask import Blueprint, request, jsonify
import os
import requests
import time
import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
from typing import List
import calendar
from deep_translator import GoogleTranslator
paper_route = Blueprint("papers", __name__)

# ------------------- NLTK 초기화 -------------------
NLTK_DATA_PATH = os.path.expanduser("~/nltk_data")
nltk.data.path = [NLTK_DATA_PATH]

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=NLTK_DATA_PATH)

# ------------------- 요약 함수 -------------------
def summarize_abstract(abstract: str, num_sentences: int = 2) -> str:
    try:
        sentences = sent_tokenize(abstract)
        if len(sentences) < 2:
            return abstract
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sim_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
        graph = nx.from_numpy_array(sim_matrix)
        scores = nx.pagerank(graph)
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        return " ".join([s for _, s in ranked_sentences[:num_sentences]])
    except Exception as e:
        print(f"[⚠️ 요약 오류] {e}")
        return abstract

# ------------------- 키워드 추출 -------------------
def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    try:
        if not text or len(text.strip()) < 10:
            return []
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([text])
        scores = zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0])
        ranked = sorted(scores, key=lambda x: x[1], reverse=True)
        return [word for word, _ in ranked[:top_n]]
    except Exception as e:
        print(f"[⚠️ 키워드 추출 오류] {e}")
        return []

# ------------------- 논문 검색 함수 -------------------
def fetch_papers(query: str, retmax: int = 5) -> List[dict]:
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json"}
    response = requests.get(search_url, params=search_params)
    id_list = response.json().get("esearchresult", {}).get("idlist", [])

    print("[🧪] PMID list:", id_list)

    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    papers = []
    month_map = {name: f"{num:02d}" for num, name in enumerate(calendar.month_abbr) if name}

    for pmid in id_list:
        fetch_params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
        try:
            fetch_response = requests.get(fetch_url, params=fetch_params)
            fetch_response.raise_for_status()
            root = ET.fromstring(fetch_response.text)

            for article in root.findall("PubmedArticle"):
                article_data = article.find(".//Article")
                if article_data is None:
                    continue

                title_en = article_data.findtext("ArticleTitle", default="(No Title)")
                abstract_nodes = article_data.findall(".//AbstractText")
                abstract = " ".join(["".join(node.itertext()).strip() for node in abstract_nodes if node is not None])
                journal = article_data.findtext(".//Journal/Title", default="Unknown Journal")

                pub_date_elem = article.find(".//PubDate")
                if pub_date_elem is not None:
                    year = pub_date_elem.findtext("Year", "")
                    month_raw = pub_date_elem.findtext("Month", "")
                    day = pub_date_elem.findtext("Day", "01")
                else:
                    year = ""
                    month_raw = ""
                    day = "01"

                month = month_map.get(month_raw[:3].capitalize(), "01") if month_raw else "01"
                pub_date = f"{year}-{month}-{day}" if year else "Unknown Date"

                article_types = [e.text for e in article.findall(".//PublicationType") if e.text] or ["Unknown Type"]
                pages = article.findtext(".//Pagination/MedlinePgn", default="")

                authors = []
                for author in article_data.findall(".//Author"):
                    first = author.findtext("ForeName")
                    last = author.findtext("LastName")
                    if first and last:
                        authors.append(f"{first} {last}")
                authors_str = authors if authors else ["Unknown Author"]

                summary = summarize_abstract(abstract)
                keywords = extract_keywords(abstract)

                papers.append({
                    "title_en": title_en,
                    "abstract": summary,
                    "abstract_full": abstract,
                    "keywords": keywords,
                    "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "authors": authors_str,
                    "journal": journal,
                    "pub_date": pub_date,
                    "pages": pages
                })

                print(f"[✅] PMID {pmid} 처리 완료: {title_en}")
                time.sleep(0.3)

        except Exception as e:
            print(f"[⚠️] PMID {pmid} 에러: {e}")
            continue

    return papers


# 번역 함수
def translate(text):
    try:
        return GoogleTranslator(source='en', target='ko').translate(text)
    except Exception as e:
        print(f"[번역 오류] {e}")
        return "(번역 실패)"


# 논문 번역 API 엔드포인트
def translate_paper(query: str, retmax: int) -> List[dict]:
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json"}

    try:
        response = requests.get(search_url, params=search_params)
        response.raise_for_status()
        id_list = response.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        return jsonify({"error": f"PubMed 검색 오류: {str(e)}"}), 500

    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    results = []
    month_map = {name: f"{num:02d}" for num, name in enumerate(calendar.month_abbr) if name}

    for pmid in id_list:
        try:
            fetch_params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
            fetch_res = requests.get(fetch_url, params=fetch_params)
            fetch_res.raise_for_status()

            root = ET.fromstring(fetch_res.text)
            article = root.find(".//PubmedArticle")
            art_data = article.find(".//Article") if article is not None else None

            if art_data is None:
                continue

            # 제목
            title_en = art_data.findtext("ArticleTitle", default="(No Title)")
            title_ko = translate(title_en)

            # 본문(추출)
            abstract_nodes = art_data.findall(".//AbstractText")
            abstract_en = " ".join(["".join(node.itertext()).strip() for node in abstract_nodes if node is not None])
            abstract_ko = translate(abstract_en)

            # 저자
            authors_en = []
            authors_ko = []
            for author in art_data.findall(".//Author"):
                first = author.findtext("ForeName")
                last = author.findtext("LastName")
                if first and last:
                    full = f"{first} {last}"
                    authors_en.append(full)
                    authors_ko.append(translate(full))

            # 유형
            type_list = article.findall(".//PublicationType")
            type = type_list[0].text if type_list else "유형 없음"

            # 저널
            journal = art_data.findtext(".//Journal/Title", default="Unknown Journal")

            # 발행일
            pub_date_elem = article.find(".//PubDate")
            if pub_date_elem is not None:
                year = pub_date_elem.findtext("Year", "")
                month_raw = pub_date_elem.findtext("Month", "")
                day = pub_date_elem.findtext("Day", "01")
            else:
                year = ""
                month_raw = ""
                day = "01"
            month = month_map.get(month_raw[:3].capitalize(), "01") if month_raw else "01"
            pub_date = f"{year}-{month}-{day}" if year else "Unknown Date"

            # 페이지
            pages = article.findtext(".//Pagination/MedlinePgn", default="")

            results.append({
                "pmid": pmid,
                "title_en": title_en,
                "title_ko": title_ko,
                "abstract_en": abstract_en,
                "abstract_ko": abstract_ko,
                "authors_en": authors_en,
                "authors_ko": authors_ko,
                "type": type,
                "journal": journal,
                "pub_date": pub_date,
                "pages": pages,
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })

            print(f"[✅] PMID {pmid} 번역 포함 완료")
            time.sleep(0.3)

        except Exception as e:
            print(f"[⚠️] PMID {pmid} 처리 중 오류: {e}")
            continue

    return results

# ------------------- 엔드포인트 -------------------
@paper_route.route("/papers", methods=["GET"])
def get_papers():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter required"}), 400
    try:
        papers = translate_paper(query=query, retmax=5)
        return jsonify({"query": query, "papers": papers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
