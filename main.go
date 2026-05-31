package main

import (
	"encoding/csv" // standard library for reading CSV
	"encoding/json"
	"fmt" // for printing errors and exiting
	"log"
	"net/http"
	"os" // for opening files

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/joho/godotenv"
)

// Problem represents one row in your CSV
type Problem struct {
	Number     string `json:"number"`
	Title      string `json:"title"`
	URL        string `json:"url"`
	Difficulty string `json:"difficulty"`
	Category   string `json:"category"`
	ExpectedTC string `json:"expected_tc"`
	MyTC       string `json:"my_tc"`
	Solved     string `json:"solved"`
	IsOptimal  string `json:"isoptimal"`
}

func main() {

	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	router := chi.NewRouter()
	router.Use(middleware.Logger)
	router.Use(middleware.Recoverer)

	router.Get("/api/problems", requireAuth(handlerGetProblems))

	// AUTH

	router.Get("/login", servePage("frontend/login.html"))
	router.Post("/login", handleLogin)
	router.Post("/logout", handleLogout)

	router.Get("/", func(w http.ResponseWriter, r *http.Request) {
		if !isLoggedIn(r) {
			http.Redirect(w, r, "/login", http.StatusSeeOther)
			return
		}
		http.ServeFile(w, r, "./frontend/index.html")
	})

	router.Patch("/api/problems/{number}", requireAuth(handlerUpdateProblem))

	fs := http.FileServer(http.Dir("./frontend"))
	router.Handle("/*", fs)

	log.Println("Server up on port 8080")
	http.ListenAndServe(":8080", router)
}

func servePage(path string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, path)
	}
}

func handlerGetProblems(w http.ResponseWriter, r *http.Request) {
	problems, err := readCSV("data/problems.csv")
	if err != nil {
		http.Error(w, "Failed in readCSV function", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")

	json.NewEncoder(w).Encode(problems)
}

func readCSV(path string) ([]Problem, error) {
	file, err := os.Open(path)
	if err != nil {
		fmt.Print(err)
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)

	rows, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var problems []Problem

	for _, row := range rows[1:] {
		p := Problem{
			Number:     row[0],
			Title:      row[1],
			URL:        row[2],
			Difficulty: row[3],
			Category:   row[4],
			ExpectedTC: row[5],
			MyTC:       row[6],
			Solved:     row[7],
			IsOptimal:  row[8],
		}
		problems = append(problems, p)
	}

	return problems, nil
}
