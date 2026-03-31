package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadSiteConfig(t *testing.T) {
	// Find the project root (where sites/ is)
	root := findProjectRoot(t)
	path := filepath.Join(root, "sites", "finance", "config.yaml")

	cfg, err := LoadSiteConfig(path)
	if err != nil {
		t.Fatalf("LoadSiteConfig: %v", err)
	}

	if cfg.Site.Name != "korean-stock-analysis" {
		t.Errorf("expected site name 'korean-stock-analysis', got %q", cfg.Site.Name)
	}
	if cfg.Site.Language != "ko" {
		t.Errorf("expected language 'ko', got %q", cfg.Site.Language)
	}
	if cfg.Deploy.Platform != "github-pages" {
		t.Errorf("expected platform 'github-pages', got %q", cfg.Deploy.Platform)
	}
	if cfg.Deploy.Framework != "docsify" {
		t.Errorf("expected framework 'docsify', got %q", cfg.Deploy.Framework)
	}
}

func TestLoadAgentConfig(t *testing.T) {
	root := findProjectRoot(t)
	path := filepath.Join(root, "sites", "finance", "agent.yaml")

	agent, err := LoadAgentConfig(path)
	if err != nil {
		t.Fatalf("LoadAgentConfig: %v", err)
	}

	if agent.Agent.Name != "finance-writer" {
		t.Errorf("expected agent name 'finance-writer', got %q", agent.Agent.Name)
	}
	if agent.Agent.Model != "claude-sonnet-4-20250514" {
		t.Errorf("expected model 'claude-sonnet-4-20250514', got %q", agent.Agent.Model)
	}
	if len(agent.Content.Types) == 0 {
		t.Error("expected content types to be non-empty")
	}
	if agent.SectorTrigger == nil {
		t.Error("expected sector_trigger to be set for finance")
	}
}

func TestLoadSite(t *testing.T) {
	root := findProjectRoot(t)
	sitePath := filepath.Join(root, "sites", "finance")

	site, err := LoadSite(sitePath)
	if err != nil {
		t.Fatalf("LoadSite: %v", err)
	}

	if site.Name != "finance" {
		t.Errorf("expected site name 'finance', got %q", site.Name)
	}
	if site.Config.Site.Name != "korean-stock-analysis" {
		t.Errorf("expected config site name 'korean-stock-analysis', got %q", site.Config.Site.Name)
	}
	if site.Agent.Agent.Name != "finance-writer" {
		t.Errorf("expected agent name 'finance-writer', got %q", site.Agent.Agent.Name)
	}
}

func TestDiscoverSites(t *testing.T) {
	root := findProjectRoot(t)
	sitesDir := filepath.Join(root, "sites")

	sites, err := DiscoverSites(sitesDir)
	if err != nil {
		t.Fatalf("DiscoverSites: %v", err)
	}

	if len(sites) < 3 {
		t.Errorf("expected at least 3 sites, got %d", len(sites))
	}

	names := make(map[string]bool)
	for _, s := range sites {
		names[s.Name] = true
	}

	for _, expected := range []string{"finance", "tech", "health"} {
		if !names[expected] {
			t.Errorf("expected site %q to be discovered", expected)
		}
	}
}

func findProjectRoot(t *testing.T) string {
	t.Helper()
	// Walk up from test file location to find go.mod
	dir, _ := os.Getwd()
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			t.Fatal("could not find project root (go.mod)")
		}
		dir = parent
	}
}
