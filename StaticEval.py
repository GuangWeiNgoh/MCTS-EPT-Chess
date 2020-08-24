import chess

# table des poids pour les pions selon leurs positions
pawntable = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, -20, -20, 10, 10,  5,
    5, -5, -10,  0,  0, -10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0,  0,  0,  0,  0,  0,  0,  0
]

# table des poids pour les cavaliers selon leurs positions
knightstable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,  0,  5,  5,  0, -20, -40,
    -30,  5, 10, 15, 15, 10,  5, -30,
    -30,  0, 15, 20, 20, 15,  0, -30,
    -30,  5, 15, 20, 20, 15,  5, -30,
    -30,  0, 10, 15, 15, 10,  0, -30,
    -40, -20,  0,  0,  0,  0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

# table des poids pour les foux selon leurs positions
bishopstable = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,  5,  0,  0,  0,  0,  5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10,  0, 10, 10, 10, 10,  0, -10,
    -10,  5,  5, 10, 10,  5,  5, -10,
    -10,  0,  5, 10, 10,  5,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

# table des poids pour les tours selon leurs positions
rookstable = [
    0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    5, 10, 10, 10, 10, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

# table des poids pour la dame selon sa position
queenstable = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  5,  5,  5,  5,  5,  0, -10,
    0,  0,  5,  5,  5,  5,  0, -5,
    -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

# table des poids pour le roi selon sa position
kingstable = [
    20, 30, 10,  0,  0, 10, 30, 20,
    20, 20,  0,  0,  0,  0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]


# On définit une fonction qui evalue le board à une instant donnée

def evaluate_board(board):

    # Traitement des cas triviaux

    # 1. Echec de blanc ou bien de noir respectivement
    if board.is_checkmate():
        if board.turn:
            return -9999
        else:
            return 9999

    # 2. Impasse ou Nul
    # Une impasse est une situation dans le jeu d’échecs où le joueur qui a le tour de jouer
    # n’est pas en échec mais n’a pas de coup légal.
    # Les règles des échecs prévoient que lorsque l’impasse se produit, le jeu se termine par un match nul.
    if board.is_stalemate():
        return 0

    # 3. Pas de pièces suffisant (i,e. juste roi vs roi)
    if board.is_insufficient_material():
        return 0

    # Calculer combien de pièces pionts, cavaliers, foux, tours, dame et roi sont restés pour le blanc et le noir

    # Nombre de pièces de type piont qui ont restés pour le blanc
    wp = len(board.pieces(chess.PAWN, chess.WHITE))

    # Nombre de pièces de type piont qui ont restés pour le noir
    bp = len(board.pieces(chess.PAWN, chess.BLACK))

    # Nombre de pièces de type cavalier qui ont restés pour le blanc
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))

    # Nombre de pièces de type cavalier qui ont restés pour le noir
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))

    # Nombre de pièces de type fou qui ont restés pour le blanc
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))

    # Nombre de pièces de type fou qui ont restés pour le fou
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))

    # Nombre de pièces de type tour qui ont restés pour le blanc
    wr = len(board.pieces(chess.ROOK, chess.WHITE))

    # Nombre de pièces de type tour qui ont restés pour le noir
    br = len(board.pieces(chess.ROOK, chess.BLACK))

    # Nombre de pièces de type dame qui ont restés pour le blanc
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))

    # Nombre de pièces de type dame qui ont restés pour le noir
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    # Calculer le score résultat du différences entre les pièces existants blancs et noirs du mêmes types
    material = 100*(wp-bp)+320*(wn-bn)+330*(wb-bb)+500*(wr-br)+900*(wq-bq)

    pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
    pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)]
                           for i in board.pieces(chess.PAWN, chess.BLACK)])

    knightsq = sum([knightstable[i]
                    for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.KNIGHT, chess.BLACK)])
    bishopsq = sum([bishopstable[i]
                    for i in board.pieces(chess.BISHOP, chess.WHITE)])
    bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.BISHOP, chess.BLACK)])
    rooksq = sum([rookstable[i]
                  for i in board.pieces(chess.ROOK, chess.WHITE)])
    rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.ROOK, chess.BLACK)])
    queensq = sum([queenstable[i]
                   for i in board.pieces(chess.QUEEN, chess.WHITE)])
    queensq = queensq + sum([-queenstable[chess.square_mirror(i)]
                             for i in board.pieces(chess.QUEEN, chess.BLACK)])
    kingsq = sum([kingstable[i]
                  for i in board.pieces(chess.KING, chess.WHITE)])
    kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.KING, chess.BLACK)])

    eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq

    return eval
    # if board.turn:
    #     return eval
    # else:
    #     return -eval