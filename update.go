package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
)

type ProblemUpdate struct {
	MyTC      string `json:"my_tc"`
	Solved    string `json:"solved"`
	IsOptimal string `json:"isoptimal"`
}

func handlerUpdateProblem(w http.ResponseWriter, r *http.Request) {
	number := chi.URLParam(r, "number")

	var update ProblemUpdate
	if err := json.NewDecoder(r.Body).Decode(&update); err != nil {
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	if err := updateCSVRow(number, update); err != nil {
		http.Error(w, "Failed to update", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func updateCSVRow(number string, update ProblemUpdate) error {
	file, err := os.Open("data/problems.csv")
	if err != nil {
		return err
	}

	rows, err := csv.NewReader(file).ReadAll()
	if err != nil {
		return err
	}

	found := false

	for i, row := range rows {
		if row[0] == number {
			rows[i][6] = update.MyTC
			rows[i][7] = update.Solved
			rows[i][8] = update.IsOptimal
			found = true
			break
		}
	}

	if !found {
		return fmt.Errorf("problem not found")
	}

	out, err := os.Create("data/problems.csv")
	if err != nil {
		return err
	}
	defer out.Close()

	writer := csv.NewWriter(out)
	defer writer.Flush()

	return writer.WriteAll(rows)
}
