from flask import Blueprint, request, jsonify
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
import requests
import urllib.parse

model_route = Blueprint("model", __name__)

@model_route.route("/compose", methods=["POST"])
def compose_model():
    try:
        data = request.get_json()
        atoms = data.get("atoms", [])
        bonds = data.get("bonds", [])

        mol = Chem.RWMol()
        atom_id_map = {}

        for atom in atoms:
            rd_atom = Chem.Atom(atom["element"])
            idx = mol.AddAtom(rd_atom)
            atom_id_map[atom["id"]] = idx

        for bond in bonds:
            a1 = atom_id_map[bond["atom1"]]
            a2 = atom_id_map[bond["atom2"]]

            bond_type = bond.get("bondType", 1)
            if bond_type == 1:
                bond_order = Chem.BondType.SINGLE
            elif bond_type == 2:
                bond_order = Chem.BondType.DOUBLE
            elif bond_type == 3:
                bond_order = Chem.BondType.TRIPLE
            else:
                bond_order = Chem.BondType.SINGLE

            mol.AddBond(a1, a2, bond_order)

        mol = mol.GetMol()
        Chem.SanitizeMol(mol)
        AllChem.EmbedMolecule(mol)
        AllChem.UFFOptimizeMolecule(mol)

        mol_block = Chem.MolToMolBlock(mol)
        smiles = Chem.MolToSmiles(mol)
        formula = rdMolDescriptors.CalcMolFormula(mol)

        name = "Unknown"
        encoded_smiles = urllib.parse.quote(smiles)
        try:
            response = requests.get(
                f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded_smiles}/property/IUPACName/JSON"
            )
            if response.status_code == 200:
                json_data = response.json()
                name = json_data['PropertyTable']['Properties'][0]['IUPACName']
        except Exception as e:
            print("PubChem 이름 조회 실패:", e)

        return jsonify({
            "mol": mol_block,
            "smiles": smiles,
            "formula": formula,
            "name": name
        }), 200

    except Exception as e:
        return jsonify({"error": f"처리 중 오류 발생: {str(e)}"}), 500



