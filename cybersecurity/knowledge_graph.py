import rdflib
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF, XSD

def build_security_kg():
    """
    Builds a simple security knowledge graph.
    """
    print("Building security knowledge graph...")
    g = Graph()

    # Define ontology for security domain (simplified OWL)
    Threat = URIRef('http://example.org/security_ontology/Threat')
    Technique = URIRef('http://example.org/security_ontology/Technique')
    Actor = URIRef('http://example.org/security_ontology/Actor')
    
    # Add concepts to the graph
    g.add((Threat, RDF.type, rdflib.RDFS.Class))
    g.add((Technique, RDF.type, rdflib.RDFS.Class))
    g.add((Actor, RDF.type, rdflib.RDFS.Class))

    # Define relationships
    uses = URIRef('http://example.org/security_ontology/uses')
    related_to = URIRef('http://example.org/security_ontology/related_to')

    # Add specific entities and relationships
    brute_force_attack = URIRef('http://example.org/security_ontology/BruteForceAttack')
    g.add((brute_force_attack, RDF.type, Threat))
    g.add((brute_force_attack, related_to, Literal("Multiple failed login attempts", datatype=XSD.string)))

    malware_campaign = URIRef('http://example.org/security_ontology/MalwareCampaign')
    g.add((malware_campaign, RDF.type, Threat))
    g.add((malware_campaign, related_to, Literal("CVE-2024-1234", datatype=XSD.string)))

    apt29 = URIRef('http://example.org/security_ontology/APT29')
    g.add((apt29, RDF.type, Actor))
    g.add((apt29, uses, brute_force_attack))

    # Example query: Find all techniques used by actor APT29
    query = """
    SELECT ?technique
    WHERE {
        <http://example.org/security_ontology/APT29> <http://example.org/security_ontology/uses> ?technique .
    }
    """
    print("\nExecuting SPARQL query...")
    for row in g.query(query):
        print(f"APT29 uses technique: {row.technique}")
    
    g.serialize("security_kg.ttl", format="turtle")
    print("Knowledge graph built and saved as 'security_kg.ttl'.")
    return g

if __name__ == "__main__":
    build_security_kg()

