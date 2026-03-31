// cmd/generate is the CLI entrypoint for content generation.
// It loads site configurations and delegates to the appropriate writer.
//
// Usage:
//
//	go run cmd/generate/main.go --site tech
//	go run cmd/generate/main.go --all
//	go run cmd/generate/main.go --site finance --type daily_briefing
package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/Reone1/blog-est/core/config"
	"github.com/spf13/cobra"
)

var (
	siteName    string
	contentType string
	outputDir   string
	allSites    bool
	context     string
)

func main() {
	rootCmd := &cobra.Command{
		Use:   "generate",
		Short: "Generate blog content for one or all sites",
		Long: `Generate blog content using Claude API based on site-specific agent.yaml configuration.

Each site defines its own tone, audience, content types, and rules in agent.yaml.
The generator loads these settings and creates appropriate content.`,
		RunE: runGenerate,
	}

	rootCmd.Flags().StringVarP(&siteName, "site", "s", "", "site name (finance, tech, health)")
	rootCmd.Flags().StringVarP(&contentType, "type", "t", "", "content type (daily_briefing, weekly_review, etc.)")
	rootCmd.Flags().StringVarP(&outputDir, "output", "o", "", "output directory (default: site's posts dir)")
	rootCmd.Flags().BoolVar(&allSites, "all", false, "generate for all sites")
	rootCmd.Flags().StringVarP(&context, "context", "c", "", "additional context for content generation")

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func runGenerate(cmd *cobra.Command, args []string) error {
	// Find project root (where go.mod is)
	root, err := findRoot()
	if err != nil {
		return fmt.Errorf("find project root: %w", err)
	}

	sitesDir := filepath.Join(root, "sites")

	if allSites {
		return generateAll(sitesDir)
	}

	if siteName == "" {
		return fmt.Errorf("specify --site <name> or --all")
	}

	return generateSite(sitesDir, siteName)
}

func generateAll(sitesDir string) error {
	sites, err := config.DiscoverSites(sitesDir)
	if err != nil {
		return fmt.Errorf("discover sites: %w", err)
	}

	fmt.Printf("Found %d sites\n", len(sites))
	for _, site := range sites {
		fmt.Printf("\n--- Generating for %s ---\n", site.Name)
		if err := generate(site); err != nil {
			fmt.Fprintf(os.Stderr, "ERROR [%s]: %v\n", site.Name, err)
			continue
		}
	}
	return nil
}

func generateSite(sitesDir, name string) error {
	site, err := config.FindSite(sitesDir, name)
	if err != nil {
		return err
	}
	return generate(site)
}

func generate(site *config.Site) error {
	fmt.Printf("Site:    %s (%s)\n", site.Config.Site.Name, site.Name)
	fmt.Printf("Agent:   %s (model: %s)\n", site.Agent.Agent.Name, site.Agent.Agent.Model)
	fmt.Printf("Tone:    %s\n", site.Agent.Persona.Tone)

	// Check if this site still uses the legacy Python pipeline
	if site.Config.Legacy != nil {
		fmt.Printf("Legacy:  using Python CLI at %s\n", site.Config.Legacy.WorkingDir)
		fmt.Println("→ Delegating to Python content_generator.cli")
		fmt.Printf("  Run: cd %s && %s --type %s --output %s\n",
			site.Config.Legacy.WorkingDir,
			site.Config.Legacy.GenerateCmd,
			contentType,
			outputDir,
		)
		// TODO: Phase 2에서 os/exec으로 실제 Python CLI 호출 구현
		return nil
	}

	// Go native generation (Phase 2+)
	if contentType == "" {
		return fmt.Errorf("specify --type for content generation")
	}

	// Validate content type against agent config
	validType := false
	for _, t := range site.Agent.Content.Types {
		if t == contentType {
			validType = true
			break
		}
	}
	if !validType {
		return fmt.Errorf("content type %q not supported for site %s (available: %v)",
			contentType, site.Name, site.Agent.Content.Types)
	}

	// TODO: Phase 2에서 core/writer/ 연동
	fmt.Printf("Content: type=%s (Go native generation not yet implemented)\n", contentType)
	fmt.Println("→ This will be implemented in Phase 2")

	return nil
}

func findRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}

	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", fmt.Errorf("go.mod not found")
		}
		dir = parent
	}
}
