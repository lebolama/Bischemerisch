from generator.sentence_transformer import translate_sentence


def run_tests():

    tests = [

        "Der Apfel ist rot",
        "Ich gehe nach Hause",
        "Das Kind spielt im Garten",
        "Der Mann arbeitet im Haus"

    ]

    for t in tests:

        result = translate_sentence(t)

        print("DE:", t)
        print("BI:", result)
        print()


if __name__ == "__main__":

    run_tests()
