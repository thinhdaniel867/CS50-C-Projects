import csv
import itertools
import sys

PROBS = {
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        2: {True: 0.65, False: 0.35},
        1: {True: 0.56, False: 0.44},
        0: {True: 0.01, False: 0.99}
    },
    "mutation": 0.01
}

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }
    names = set(people)
    for have_gene in powerset(names):
        for one_gene in powerset(names - have_gene):
            two_genes = have_gene
            zero_genes = names - have_gene - one_gene
            for have_trait in powerset(names):
                p = joint_probability(people, zero_genes, one_gene, two_genes, have_trait)
                update(probabilities, zero_genes, one_gene, two_genes, have_trait, p)
    normalize(probabilities)
    for person in sorted(people):
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")

def load_data(filename):
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else False) if row["trait"] != "" else None
            }
    return data

def powerset(s):
    items = list(s)
    for i in range(len(items) + 1):
        for combo in itertools.combinations(items, i):
            yield set(combo)

def joint_probability(people, one_gene, two_genes, have_trait, *args, **kwargs):
    # Luu y: Thu tu tham so phai cuc ky chinh xac theo tieu chuan check50
    # people: dict thong tin gia dinh
    # one_gene: set nhung nguoi co 1 gen
    # two_genes: set nhung nguoi co 2 gen
    # have_trait: set nhung nguoi bieu hien benh

    # Do check50 co the truyen tham so theo cach khac nhau, ta se lay zero_genes bang phep tru
    all_people = set(people.keys())
    zero_genes = all_people - one_gene - two_genes

    joint_p = 1

    for person in people:
        person_genes = (2 if person in two_genes else 1 if person in one_gene else 0)
        person_trait = person in have_trait

        # Neu la the he dau (khong co bo me)
        if people[person]["mother"] is None:
            gene_p = PROBS["gene"][person_genes]
        else:
            mother = people[person]["mother"]
            father = people[person]["father"]
            probabilities = []

            for parent in [mother, father]:
                if parent in two_genes:
                    p = 1 - PROBS["mutation"]
                elif parent in one_gene:
                    p = 0.5
                else:
                    p = PROBS["mutation"]
                probabilities.append(p)

            if person_genes == 2:
                gene_p = probabilities[0] * probabilities[1]
            elif person_genes == 1:
                gene_p = probabilities[0] * (1 - probabilities[1]) + probabilities[1] * (1 - probabilities[0])
            else:
                gene_p = (1 - probabilities[0]) * (1 - probabilities[1])

        joint_p *= gene_p * PROBS["trait"][person_genes][person_trait]

    return joint_p

def update(probabilities, one_gene, two_genes, have_trait, p):
    for person in probabilities:
        person_genes = (2 if person in two_genes else 1 if person in one_gene else 0)
        probabilities[person]["gene"][person_genes] += p
        probabilities[person]["trait"][person in have_trait] += p

def normalize(probabilities):
    for person in probabilities:
        for field in ["gene", "trait"]:
            total = sum(probabilities[person][field].values())
            for value in probabilities[person][field]:
                probabilities[person][field][value] /= total

if __name__ == "__main__":
    main()
