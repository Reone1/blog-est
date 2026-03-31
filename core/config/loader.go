package config

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"gopkg.in/yaml.v3"
)

// LoadSite loads both config.yaml and agent.yaml for a given site directory.
func LoadSite(sitePath string) (*Site, error) {
	name := filepath.Base(sitePath)

	cfg, err := LoadSiteConfig(filepath.Join(sitePath, "config.yaml"))
	if err != nil {
		return nil, fmt.Errorf("load config.yaml for %s: %w", name, err)
	}

	agent, err := LoadAgentConfig(filepath.Join(sitePath, "agent.yaml"))
	if err != nil {
		return nil, fmt.Errorf("load agent.yaml for %s: %w", name, err)
	}

	return &Site{
		Name:     name,
		Path:     sitePath,
		Config:   *cfg,
		Agent:    *agent,
		LoadedAt: time.Now(),
	}, nil
}

// LoadSiteConfig parses a config.yaml file.
func LoadSiteConfig(path string) (*SiteConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read %s: %w", path, err)
	}

	var cfg SiteConfig
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("parse %s: %w", path, err)
	}

	return &cfg, nil
}

// LoadAgentConfig parses an agent.yaml file.
func LoadAgentConfig(path string) (*AgentConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read %s: %w", path, err)
	}

	var cfg AgentConfig
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("parse %s: %w", path, err)
	}

	return &cfg, nil
}

// DiscoverSites scans the sites/ directory and loads all site configurations.
func DiscoverSites(sitesDir string) ([]*Site, error) {
	entries, err := os.ReadDir(sitesDir)
	if err != nil {
		return nil, fmt.Errorf("read sites dir %s: %w", sitesDir, err)
	}

	var sites []*Site
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}

		sitePath := filepath.Join(sitesDir, entry.Name())

		// Skip directories without config.yaml
		if _, err := os.Stat(filepath.Join(sitePath, "config.yaml")); os.IsNotExist(err) {
			continue
		}

		site, err := LoadSite(sitePath)
		if err != nil {
			return nil, err
		}

		sites = append(sites, site)
	}

	return sites, nil
}

// FindSite loads a specific site by name from the sites/ directory.
func FindSite(sitesDir, name string) (*Site, error) {
	sitePath := filepath.Join(sitesDir, name)

	if _, err := os.Stat(sitePath); os.IsNotExist(err) {
		return nil, fmt.Errorf("site %q not found in %s", name, sitesDir)
	}

	return LoadSite(sitePath)
}
