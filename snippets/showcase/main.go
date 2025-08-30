package showcase

import (
	"fmt"
	"time"
)

type Artifact struct {
	ID          int
	Name        string
	Description string
}

func (a *Artifact) Display() {
	if a == nil {
		fmt.Println("Cannot display a nil artifact.")
		return
	}
	fmt.Printf("Artifact #%d: %s\n", a.ID, a.Name)
	fmt.Printf("\t\"%s\"\n", a.Description)
}

func main() {
	inventory := []Artifact{
		{1, "Kintsugi VS Code Theme", "A theme for developers who see code as a craft."},
		{2, "Minimalist Icon Set", "An elegant companion for a focused workspace."},
	}

	for i := range inventory {
		inventory[i].Display()
	}

	time.Sleep(100 * time.Millisecond)
	fmt.Println("\nCrafting complete.")
}
