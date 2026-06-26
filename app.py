import json
import math
import threading
import tkinter as tk
import urllib.parse
import urllib.request

WEATHER_CODE_MAP = {
    0: ("Clear sky", "☀️", "#f59e0b"),
    1: ("Mainly clear", "🌤️", "#38bdf8"),
    2: ("Partly cloudy", "⛅", "#60a5fa"),
    3: ("Overcast", "☁️", "#64748b"),
    45: ("Fog", "🌫️", "#94a3b8"),
    48: ("Depositing rime fog", "🌫️", "#94a3b8"),
    51: ("Light drizzle", "🌦️", "#38bdf8"),
    53: ("Moderate drizzle", "🌦️", "#38bdf8"),
    55: ("Dense drizzle", "🌧️", "#0ea5e9"),
    56: ("Freezing drizzle", "🌧️", "#38bdf8"),
    57: ("Freezing drizzle", "🌧️", "#38bdf8"),
    61: ("Light rain", "🌧️", "#0284c7"),
    63: ("Moderate rain", "🌧️", "#0369a1"),
    65: ("Heavy rain", "⛈️", "#014f86"),
    66: ("Freezing rain", "🌧️", "#38bdf8"),
    67: ("Freezing rain", "🌧️", "#38bdf8"),
    71: ("Light snow", "🌨️", "#c7d2fe"),
    73: ("Snow", "❄️", "#e2e8f0"),
    75: ("Heavy snow", "❄️", "#cbd5e1"),
    77: ("Snow grains", "🌨️", "#c7d2fe"),
    80: ("Rain showers", "🌧️", "#0ea5e9"),
    81: ("Moderate showers", "🌧️", "#0284c7"),
    82: ("Violent showers", "⛈️", "#075985"),
    85: ("Snow showers", "🌨️", "#c7d2fe"),
    86: ("Heavy snow showers", "🌨️", "#c7d2fe"),
    95: ("Thunderstorm", "⛈️", "#0f172a"),
    96: ("Thunderstorm", "⛈️", "#0f172a"),
    99: ("Thunderstorm", "⛈️", "#0f172a"),
}


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather Explorer")
        self.geometry("440x580")
        self.resizable(False, False)
        self.configure(bg="#0f172a")

        self.city_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Search a city to see current weather")

        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self, bg="#0f172a")
        header.pack(fill="x", padx=20, pady=(18, 4))

        tk.Label(
            header,
            text="Weather Explorer",
            fg="white",
            bg="#0f172a",
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="City search, live temperature, and stylish weather cards",
            fg="#cbd5e1",
            bg="#0f172a",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        search_frame = tk.Frame(self, bg="#0f172a")
        search_frame.pack(fill="x", padx=20, pady=10)

        entry = tk.Entry(
            search_frame,
            textvariable=self.city_var,
            font=("Segoe UI", 14),
            bd=0,
            relief="flat",
            bg="#1e293b",
            fg="white",
            insertbackground="white",
        )
        entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        entry.bind("<Return>", self.search_weather)

        self.search_button = tk.Button(
            search_frame,
            text="Search",
            command=self.search_weather,
            font=("Segoe UI", 12, "bold"),
            bg="#38bdf8",
            fg="#0f172a",
            activebackground="#22d3ee",
            bd=0,
            relief="flat",
            padx=20,
            pady=10,
        )
        self.search_button.pack(side="right")

        status = tk.Label(
            self,
            textvariable=self.status_var,
            fg="#94a3b8",
            bg="#0f172a",
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        )
        status.pack(fill="x", padx=20, pady=(0, 10))

        self.weather_card = tk.Frame(self, bg="#1e293b", bd=0, relief="flat")
        self.weather_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.card_top = tk.Frame(self.weather_card, bg="#1e293b")
        self.card_top.pack(fill="x", pady=20, padx=20)

        self.location_label = tk.Label(
            self.card_top,
            text="--",
            fg="white",
            bg="#1e293b",
            font=("Segoe UI", 18, "bold"),
        )
        self.location_label.pack(anchor="w")

        self.condition_label = tk.Label(
            self.card_top,
            text="Awaiting weather...",
            fg="#cbd5e1",
            bg="#1e293b",
            font=("Segoe UI", 12),
        )
        self.condition_label.pack(anchor="w", pady=(4, 0))

        self.temperature_label = tk.Label(
            self.weather_card,
            text="0.0°C / 32.0°F",
            fg="white",
            bg="#1e293b",
            font=("Segoe UI", 44, "bold"),
        )
        self.temperature_label.pack(pady=(10, 0))

        self.icon_canvas = tk.Canvas(
            self.weather_card,
            width=160,
            height=160,
            bg="#1e293b",
            highlightthickness=0,
        )
        self.icon_canvas.pack(pady=(0, 10))

        metric_frame = tk.Frame(self.weather_card, bg="#1e293b")
        metric_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.feels_label = tk.Label(
            metric_frame,
            text="Wind: -- km/h",
            fg="#e2e8f0",
            bg="#1e293b",
            font=("Segoe UI", 11),
        )
        self.feels_label.grid(row=0, column=0, sticky="w")

        self.humidity_label = tk.Label(
            metric_frame,
            text="Humidity: -- %",
            fg="#e2e8f0",
            bg="#1e293b",
            font=("Segoe UI", 11),
        )
        self.humidity_label.grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.wind_label = tk.Label(
            metric_frame,
            text="Direction: --°",
            fg="#e2e8f0",
            bg="#1e293b",
            font=("Segoe UI", 11),
        )
        self.wind_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

        metric_frame.columnconfigure(0, weight=1)

    def search_weather(self, event=None):
        city = self.city_var.get().strip()
        if not city:
            self.set_status("Type a city name and press Search.", error=True)
            return

        self.set_status("Looking up city and weather…")
        self.search_button.config(state="disabled")
        threading.Thread(target=self.fetch_weather, args=(city,), daemon=True).start()

    def set_status(self, message, error=False):
        self.status_var.set(message)
        self.status_var_label = "#f87171" if error else "#94a3b8"
        self.update_idletasks()

    def fetch_weather(self, city):
        try:
            location = self.geocode_city(city)
            if not location:
                raise ValueError("City not found. Try another name.")

            weather = self.get_current_weather(location)
            self.after(0, lambda: self.render_weather(location, weather))
        except Exception as exc:
            self.after(0, lambda: self.show_error(str(exc)))

    def geocode_city(self, city):
        query = urllib.parse.quote_plus(city)
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
        data = self.fetch_json(url)
        results = data.get("results") or []
        return results[0] if results else None

    def get_current_weather(self, location):
        lat = location["latitude"]
        lon = location["longitude"]
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current_weather=true&hourly=relativehumidity_2m&timezone=auto"
        )
        data = self.fetch_json(url)
        current = data.get("current_weather")
        if not current:
            raise ValueError("Unable to retrieve weather details.")

        humidity = 0
        hourly = data.get("hourly", {})
        if hourly and "time" in hourly and "relativehumidity_2m" in hourly:
            times = hourly["time"]
            humidity_levels = hourly["relativehumidity_2m"]
            if current["time"] in times:
                index = times.index(current["time"])
                humidity = humidity_levels[index]

        current["humidity"] = humidity
        return current

    def fetch_json(self, url):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "WeatherExplorer/1.0"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    def render_weather(self, location, weather):
        code = weather.get("weathercode", 0)
        condition, icon, accent = WEATHER_CODE_MAP.get(code, ("Unknown", "❔", "#64748b"))
        celsius = weather.get("temperature", 0.0)
        fahrenheit = celsius * 9 / 5 + 32

        self.location_label.config(text=f"{location.get('name')}, {location.get('country', '')}")
        self.condition_label.config(text=f"{icon}  {condition}")
        self.temperature_label.config(text=f"{celsius:.1f}°C / {fahrenheit:.1f}°F")
        self.feels_label.config(text=f"Wind: {weather.get('windspeed', 0):.0f} km/h")
        self.humidity_label.config(text=f"Humidity: {weather.get('humidity', 0):.0f}%")
        self.wind_label.config(text=f"Direction: {weather.get('winddirection', 0):.0f}°")

        self.draw_icon(icon, accent)
        self.set_status("Weather updated successfully.")
        self.search_button.config(state="normal")

    def draw_icon(self, icon, accent):
        self.icon_canvas.delete("all")
        self.icon_canvas.create_oval(10, 10, 150, 150, fill=accent, outline="")
        self.icon_canvas.create_text(
            80,
            80,
            text=icon,
            font=("Segoe UI Emoji", 48),
            fill="#0f172a",
        )
        self.icon_canvas.create_text(
            80,
            140,
            text="Current",
            font=("Segoe UI", 10, "bold"),
            fill="#e2e8f0",
        )

    def show_error(self, message):
        self.status_var.set(message)
        self.search_button.config(state="normal")


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
