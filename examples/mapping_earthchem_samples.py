#!/usr/bin/env python
""" file: mapping_earthchem_samples.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagshi
    date:   4 August 2014

    description: Example showing usage of EarthChem REST API
"""

from pysiss.vocabulary.lithology.composition import EarthChemQuery
import folium

def main():
    query = EarthChemQuery()
    print query
    print query.url

if __name__ == '__main__':
    main()