from fastapi import FastAPI
from blockchain import Blockchain
from pydantic import BaseModel
from typing import List,Optional
from uuid import uuid4
app = FastAPI()

# Создаем экземпляр блокчейна
blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')


class NewTransaction(BaseModel):
    nodes: str
    recipient: str
    amount: int

class NewNode(BaseModel):
    nodes:Optional[List[str]]  = None

@app.get('/mine')
def mine():
    # Мы запускаем алгоритм подтверждения работы, чтобы получить следующее подтверждение…
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Мы должны получить вознаграждение за найденное подтверждение
    # Отправитель “0” означает, что узел заработал крипто-монету
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Создаем новый блок, путем внесения его в цепь
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return response


@app.post('/transactions/new')
def new_transaction(values: NewTransaction):

    # Создание новой транзакции
    index = blockchain.new_transaction(
        values.sender, values.recipient, values.amount)

    response = {'message': f'Transaction will be added to Block {index}'}
    return response


@app.post('/chain')
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return response

@app.post('/nodes/register')
def register_nodes(values : NewNode):
    
 
    nodes = values.nodes
    if nodes is None:
        return "Error: Please supply a valid list of nodes"
 
    for node in nodes:
        blockchain.register_node(node)
 
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return response
 
 
@app.get('/nodes/resolve')
def consensus():
    replaced = blockchain.resolve_conflicts()
 
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
 
    return response