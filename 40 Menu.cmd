def menu():
    ops = [
        ("1", "azul", '1 --cores "#1278ff"'),
        ("2", "vermelho", '1 --cores "#ff2b2b"'),
        ("3", "duas cores", '2 --cores "#ff2d2d,#2df0ff"'),
        ("4", "fusao", '3 --metaball'),
        ("5", "cor cheia", '1 --cor-cheia'),
        ("6", "chuva", '2 --fundo chuva --cores "#00ff66"'),
        ("7", "suas cores", ''),
    ]
    print("efeitos:")
    for k, nome, _ in ops:
        print("  %s - %s" % (k, nome))
    escolha = input("opcao: ").strip()
    alvo = dict((k, a) for k, n, a in ops).get(escolha)
    if alvo is None:
        return 1
    argv = ["esfera.py"] + alvo.split()
    if escolha == "7":
        c = input("cores (ex: #ff0000,#00ff00): ").strip()
        argv += ["--cores", c]
    sys.argv = argv
    return main()
