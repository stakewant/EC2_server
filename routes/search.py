from flask import Blueprint, request, jsonify
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
import requests
import urllib.parse

search_route = Blueprint("search", __name__)

@search_route.route("/from_name", methods=["GET"])
def from_name():
    name = request.args.get("name")
    if not name:
        return jsonify({'error': 'name parameter required'}), 400

    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(name)}/record/SDF/?record_type=3d"
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({'error': 'Compound not found'}), 404

        mol = Chem.MolFromMolBlock(response.text)
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol)
        AllChem.UFFOptimizeMolecule(mol)

        mol_block = Chem.MolToMolBlock(mol)
        smiles = Chem.MolToSmiles(mol)
        formula = rdMolDescriptors.CalcMolFormula(mol)

        return jsonify({
            "mol": mol_block,
            "smiles": smiles,
            "formula": formula,
            "name": name
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

