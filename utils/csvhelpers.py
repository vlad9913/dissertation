import csv
import random
import string


def generate_random_name():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(10))


def generate_random_energy():
    return random.uniform(0, 1)


def write_to_csv(filename, num_lines):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'Energy'])

        for _ in range(num_lines):
            name = generate_random_name()
            energy = generate_random_energy()
            writer.writerow([name, energy])



