from src.global_store import get_custom_labels, get_label_id
import os


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    names_txt_path = os.path.join(root_dir, 'data', 'names.txt')

    custom_labels = get_custom_labels()

    with open(names_txt_path, 'r') as f:
        names = [line.strip() for line in f]
        print("count in names.txt: ", len(names))
        print("count in global_store: ", len(custom_labels))
        for label_name in names:
            label_id = get_label_id(label_name)
            if not label_id:
                print("error")


if __name__ == '__main__':
    main()
