import tkinter as tk
from tkinter import messagebox
import random

BOARD_SIZE = 8
CELL_SIZE = 80

EMPTY = None
RED = "red"
BLACK = "black"


class CheckersPro:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 CHECKERS PRO 🔥")

        self.difficulty = tk.StringVar(value="Normal")

        self.create_menu()
        self.create_board_ui()

        self.start_game()

    # ================= UI =================
    def create_menu(self):
        top = tk.Frame(self.root)
        top.pack(pady=5)

        tk.Label(top, text="Difficulty:", font=("Arial", 11)).pack(side=tk.LEFT)

        tk.OptionMenu(
            top,
            self.difficulty,
            "Mudah",
            "Normal",
            "Sulit"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            top,
            text="🔄 Restart",
            command=self.start_game
        ).pack(side=tk.LEFT, padx=10)

        self.status = tk.Label(
            self.root,
            text="",
            font=("Arial", 12, "bold")
        )
        self.status.pack()

    def create_board_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            width=BOARD_SIZE * CELL_SIZE,
            height=BOARD_SIZE * CELL_SIZE,
            bg="white"
        )
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_click)

    # ================= GAME =================
    def start_game(self):
        self.board = [[EMPTY for _ in range(8)] for _ in range(8)]

        for r in range(3):
            for c in range(8):
                if (r + c) % 2:
                    self.board[r][c] = {"color": BLACK, "king": False}

        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2:
                    self.board[r][c] = {"color": RED, "king": False}

        self.current_player = RED
        self.selected = None
        self.valid_moves = []
        self.chain_piece = None  # penting untuk multi eat

        self.update_status()
        self.draw_board()

    # ================= DRAW =================
    def draw_board(self):
        self.canvas.delete("all")

        for r in range(8):
            for c in range(8):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                color = "#B58863" if (r + c) % 2 else "#F0D9B5"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.board[r][c]
                if piece:
                    self.canvas.create_oval(
                        x1 + 10, y1 + 10,
                        x2 - 10, y2 - 10,
                        fill=piece["color"],
                        outline="black",
                        width=2
                    )

                    if piece["king"]:
                        self.canvas.create_text(
                            (x1+x2)//2,
                            (y1+y2)//2,
                            text="👑",
                            font=("Arial", 24)
                        )

        if self.selected:
            r, c = self.selected
            self.canvas.create_rectangle(
                c*CELL_SIZE, r*CELL_SIZE,
                (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                outline="blue", width=3
            )

        for r, c in self.valid_moves:
            self.canvas.create_oval(
                c*CELL_SIZE+30,
                r*CELL_SIZE+30,
                c*CELL_SIZE+50,
                r*CELL_SIZE+50,
                fill="yellow"
            )

    # ================= STATUS =================
    def update_status(self):
        turn = "MERAH (Kamu)" if self.current_player == RED else "HITAM (AI)"
        self.status.config(text=f"Giliran: {turn}")

    # ================= CLICK =================
    def on_click(self, event):
        if self.current_player != RED:
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if self.selected and (row, col) in self.valid_moves:
            sr, sc = self.selected
            captured = self.make_move(sr, sc, row, col)

            # cek apakah bisa makan lagi
            more = self.get_captures(row, col, RED)

            if captured and more:
                self.selected = (row, col)
                self.valid_moves = more
                self.draw_board()
                return

            self.selected = None
            self.valid_moves = []

            self.current_player = BLACK
            self.update_status()
            self.draw_board()
            self.root.after(400, self.ai_move)
            return

        piece = self.board[row][col]

        if piece and piece["color"] == RED:
            captures = self.get_captures(row, col, RED)

            self.selected = (row, col)
            self.valid_moves = captures if captures else self.get_moves(row, col, RED)
        else:
            self.selected = None
            self.valid_moves = []

        self.draw_board()

    # ================= MOVE LOGIC =================
    def get_moves(self, r, c, player):
        piece = self.board[r][c]
        moves = []

        if piece["king"]:
            directions = [(-1,-1),(-1,1),(1,-1),(1,1)]

            for dr, dc in directions:
                step = 1
                while True:
                    tr = r + dr*step
                    tc = c + dc*step

                    if not (0 <= tr < 8 and 0 <= tc < 8):
                        break

                    if self.board[tr][tc] is EMPTY:
                        moves.append((tr, tc))
                    else:
                        break

                    step += 1
        else:
            forward = -1 if player == RED else 1

            for dc in [-1, 1]:
                tr, tc = r+forward, c+dc
                if 0 <= tr < 8 and 0 <= tc < 8:
                    if self.board[tr][tc] is EMPTY:
                        moves.append((tr, tc))

        return moves

    # ⭐ FUNGSI MAKAN (INTI UPGRADE)
    def get_captures(self, r, c, player):
        piece = self.board[r][c]
        opponent = BLACK if player == RED else RED
        captures = []

        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]

        # ===== KING =====
        if piece["king"]:
            for dr, dc in directions:
                step = 1
                enemy_found = False

                while True:
                    tr = r + dr*step
                    tc = c + dc*step

                    if not (0 <= tr < 8 and 0 <= tc < 8):
                        break

                    target = self.board[tr][tc]

                    if target and target["color"] == opponent and not enemy_found:
                        enemy_found = True

                    elif target is EMPTY and enemy_found:
                        captures.append((tr, tc))

                    elif target is not EMPTY:
                        break

                    step += 1

        # ===== BIDAK BIASA =====
        else:
            forward = -1 if player == RED else 1

            for dc in [-1,1]:
                mr = r + forward
                mc = c + dc
                tr = r + forward*2
                tc = c + dc*2

                if 0 <= tr < 8 and 0 <= tc < 8:
                    mid = self.board[mr][mc]

                    if mid and mid["color"] == opponent and self.board[tr][tc] is EMPTY:
                        captures.append((tr, tc))

        return captures

    def make_move(self, sr, sc, tr, tc):
        piece = self.board[sr][sc]
        self.board[tr][tc] = piece
        self.board[sr][sc] = EMPTY

        captured = False

        dr = tr - sr
        dc = tc - sc

        step_r = (dr//abs(dr)) if dr != 0 else 0
        step_c = (dc//abs(dc)) if dc != 0 else 0

        r, c = sr + step_r, sc + step_c

        while (r, c) != (tr, tc):
            if self.board[r][c] is not EMPTY:
                self.board[r][c] = EMPTY
                captured = True
                break
            r += step_r
            c += step_c

        if piece["color"] == RED and tr == 0:
            piece["king"] = True
        if piece["color"] == BLACK and tr == 7:
            piece["king"] = True

        return captured

    # ================= AI =================
    def ai_move(self):
        moves = []
        captures_exist = False

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece["color"] == BLACK:

                    captures = self.get_captures(r, c, BLACK)
                    if captures:
                        captures_exist = True
                        for tr, tc in captures:
                            moves.append((r,c,tr,tc))
                    elif not captures_exist:
                        for tr, tc in self.get_moves(r, c, BLACK):
                            moves.append((r,c,tr,tc))

        if not moves:
            messagebox.showinfo("MENANG!", "🔥 Kamu Mengalahkan AI!")
            return

        move = random.choice(moves)

        r, c, tr, tc = move
        captured = self.make_move(r, c, tr, tc)

        # chain eat AI
        while captured:
            more = self.get_captures(tr, tc, BLACK)
            if not more:
                break

            tr2, tc2 = random.choice(more)
            captured = self.make_move(tr, tc, tr2, tc2)
            tr, tc = tr2, tc2

        self.current_player = RED
        self.update_status()
        self.draw_board()


if __name__ == "__main__":
    root = tk.Tk()
    CheckersPro(root)
    root.mainloop()
