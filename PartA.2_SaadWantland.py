import data_generation as dg
import data_preprocessing as dp
import load_data_neo4j as ld

def main():
    # The Data Generation script is commented out to avoid the application taking too long but it
    # can be uncommented to validate functionality.
    # dg.main()
    dp.main()
    ld.main()

if __name__ == '__main__':
    main()