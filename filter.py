import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import requests
import io

class ChessDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Satranç Veri Tabanı Filtreleme Uygulaması")
        self.root.geometry("800x600")

        self.create_widgets()
        self.data = None
        self.filtered_data = None

    def create_widgets(self):
        platform_label = tk.Label(self.root, text="Oyun Platformu:")
        platform_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.platform_var = tk.StringVar(value="Her İkisi")
        platform_dropdown = ttk.Combobox(
            self.root, textvariable=self.platform_var, values=["Lichess", "Chess.com", "Her İkisi"]
        )
        platform_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        date_label = tk.Label(self.root, text="Oyun Tarihi Aralığı (YYYY-MM-DD):")
        date_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        start_date_entry = tk.Entry(self.root, textvariable=self.start_date_var)
        end_date_entry = tk.Entry(self.root, textvariable=self.end_date_var)
        start_date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        end_date_entry.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        elo_label = tk.Label(self.root, text="Elo Aralığı (Min-Max):")
        elo_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.min_elo_var = tk.StringVar(value="1000")
        self.max_elo_var = tk.StringVar(value="3000")
        min_elo_entry = tk.Entry(self.root, textvariable=self.min_elo_var)
        max_elo_entry = tk.Entry(self.root, textvariable=self.max_elo_var)
        min_elo_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        max_elo_entry.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        filter_button = tk.Button(self.root, text="Filtrele ve Verileri İndir", command=self.fetch_and_filter_data)
        filter_button.grid(row=3, column=1, padx=10, pady=20)

        save_button = tk.Button(self.root, text="Sonuçları CSV'ye Kaydet", command=self.save_to_csv)
        save_button.grid(row=3, column=2, padx=10, pady=20)

    def fetch_lichess_games(self, username, token):
        url = f"https://lichess.org/api/games/user/{username}"
        headers = {'Authorization': f'Bearer {token}'}
        params = {'max': 100, 'pgnInJson': True}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def fetch_chesscom_games(self, username):
        url = f"https://api.chess.com/pub/player/{username}/games/archives"
        response = requests.get(url)
        if response.status_code == 200:
            archives = response.json()['archives']
            all_games = []
            for archive_url in archives:
                games_response = requests.get(archive_url)
                if games_response.status_code == 200:
                    all_games.extend(games_response.json()['games'])
            return all_games
        else:
            return []

    def fetch_and_filter_data(self):
        platform = self.platform_var.get()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        min_elo = int(self.min_elo_var.get())
        max_elo = int(self.max_elo_var.get())

        games = []
        if platform in ["Lichess", "Her İkisi"]:
            lichess_games = self.fetch_lichess_games("username", "your_lichess_token")
            games.extend(lichess_games)

        if platform in ["Chess.com", "Her İkisi"]:
            chesscom_games = self.fetch_chesscom_games("username")
            games.extend(chesscom_games)

        filtered_games = [
            game for game in games
            if min_elo <= game.get('white_elo', 0) <= max_elo
            and start_date <= game.get('date', '') <= end_date
        ]

        self.filtered_data = pd.DataFrame(filtered_games)

    def save_to_csv(self):
        if self.filtered_data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                self.filtered_data.to_csv(file_path, index=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessDatabaseApp(root)
    root.mainloop()
