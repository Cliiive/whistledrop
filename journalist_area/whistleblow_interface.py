import argparse

#from src.rsa_key_generator import
#from src.rsa_key_uploader import

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generiert mehrere RSA-Schlüsselpaare.")

    parser.add_argument(
        "-n", "--number",
        type=int,
        default=1,
        help="Anzahl der Schlüsselpaare (Standard: 1)"
    )

    parser.add_argument(
        "-s", "--size",
        type=int,
        default=2048,
        help="Schlüssellänge in Bit (Standard: 2048)"
    )

    args = parser.parse_args()

    # print("Number: ", args.number, " | Size of Key: ", args.size)
    key = generate_multiple_keys(count=args.number, key_size=args.size)

    write_keys_to_database(keys=key)