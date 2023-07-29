from neo4j import GraphDatabase
from secret import Secret


class Email:
    emails = set()

    def read_emails():
        neo4j_uri = Secret.neo4j_URI  # Replace with your Neo4j URI
        neo4j_user = Secret.neo4j_USER  # Replace with your Neo4j username
        neo4j_password = Secret.neo4j_PW  # Replace with your Neo4j password

        with GraphDatabase.driver(neo4j_uri,
                                  auth=(neo4j_user, neo4j_password)) as driver:
            with driver.session() as session:
                result = session.read_transaction(Email.get_emails)
                return result

    def get_emails(tx):
        result = tx.run("MATCH (e:Email) RETURN e.email AS email")
        return list({record["email"] for record in result})
