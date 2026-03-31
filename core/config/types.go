// Package config provides configuration types and loaders for the blog-est monorepo.
// Each site (finance, tech, health) has a config.yaml (infrastructure) and agent.yaml (behavior).
package config

import "time"

// SiteConfig represents a site's infrastructure configuration (config.yaml).
type SiteConfig struct {
	Site     SiteInfo     `yaml:"site"`
	Deploy   DeployConfig `yaml:"deploy"`
	Publish  PublishConfig `yaml:"publish"`
	Legacy   *LegacyConfig `yaml:"legacy,omitempty"`
	Schedule ScheduleConfig `yaml:"schedule"`
	SEO      SEOConfig    `yaml:"seo"`
}

type SiteInfo struct {
	Name        string `yaml:"name"`
	Domain      string `yaml:"domain"`
	Language    string `yaml:"language"`
	Description string `yaml:"description"`
}

type DeployConfig struct {
	Platform  string `yaml:"platform"`  // "vercel" | "github-pages"
	Framework string `yaml:"framework"` // "docsify"
	Root      string `yaml:"root"`
	BaseURL   string `yaml:"base_url"`
}

type PublishConfig struct {
	Target      string `yaml:"target"`       // "docsify" | "wordpress"
	PostsDir    string `yaml:"posts_dir"`
	SidebarFile string `yaml:"sidebar_file"`
	SitemapFile string `yaml:"sitemap_file"`
}

// LegacyConfig holds paths for the existing Python-based pipeline.
// Used during the migration period (Phase 0~1).
type LegacyConfig struct {
	WorkingDir  string `yaml:"working_dir"`
	GenerateCmd string `yaml:"generate_cmd"`
	SidebarCmd  string `yaml:"sidebar_cmd"`
	SitemapCmd  string `yaml:"sitemap_cmd"`
}

type ScheduleConfig struct {
	ContentGeneration string `yaml:"content_generation,omitempty"`
	DailyBriefing     string `yaml:"daily_briefing,omitempty"`
	WeeklyReview      string `yaml:"weekly_review,omitempty"`
	MonthlyReview     string `yaml:"monthly_review,omitempty"`
	KeywordCrawl      string `yaml:"keyword_crawl,omitempty"`
	Report            string `yaml:"report,omitempty"`
}

type SEOConfig struct {
	Sitemap       bool   `yaml:"sitemap"`
	RobotsTxt     bool   `yaml:"robots_txt"`
	CanonicalBase string `yaml:"canonical_base"`
	OGImage       string `yaml:"og_image,omitempty"`
}

// AgentConfig represents a site's agent behavior configuration (agent.yaml).
type AgentConfig struct {
	Agent          AgentInfo       `yaml:"agent"`
	Persona        PersonaConfig   `yaml:"persona"`
	Content        ContentConfig   `yaml:"content"`
	Rules          RulesConfig     `yaml:"rules"`
	SectorTrigger  *SectorTrigger  `yaml:"sector_trigger,omitempty"`
	Keywords       *KeywordsConfig `yaml:"keywords,omitempty"`
	DataSources    *DataSources    `yaml:"data_sources,omitempty"`
	Affiliate      AffiliateConfig `yaml:"affiliate"`
}

type AgentInfo struct {
	Name  string `yaml:"name"`
	Model string `yaml:"model"`
}

type PersonaConfig struct {
	Tone     string `yaml:"tone"`
	Audience string `yaml:"audience"`
	Style    string `yaml:"style"`
	Niche    string `yaml:"niche"`
}

type ContentConfig struct {
	Types     []string               `yaml:"types"`
	WordCount map[string]WordRange   `yaml:"word_count"`
	Structure ContentStructure       `yaml:"structure"`
}

type WordRange struct {
	Min int `yaml:"min"`
	Max int `yaml:"max"`
}

type ContentStructure struct {
	IncludeTOC          bool `yaml:"include_toc"`
	IncludeTLDR         bool `yaml:"include_tldr"`
	IncludeCodeExamples bool `yaml:"include_code_examples,omitempty"`
	IncludeReferences   bool `yaml:"include_references,omitempty"`
	IncludeDisclaimer   bool `yaml:"include_disclaimer,omitempty"`
	Language            string `yaml:"language,omitempty"`
}

type RulesConfig struct {
	Must  []string `yaml:"must"`
	Avoid []string `yaml:"avoid"`
}

// SectorTrigger defines conditions for auto-generating sector analysis (finance site).
type SectorTrigger struct {
	Conditions []string `yaml:"conditions"`
	MatchAny   bool     `yaml:"match_any"`
}

type KeywordsConfig struct {
	Strategy      string  `yaml:"strategy"`
	MinVolume     int     `yaml:"min_volume"`
	MaxDifficulty float64 `yaml:"max_difficulty"`
	SeedFile      string  `yaml:"seed_file"`
}

type DataSources struct {
	KoreanMarket *MarketSource    `yaml:"korean_market,omitempty"`
	USMarket     *MarketSource    `yaml:"us_market,omitempty"`
	Analytics    *AnalyticsSource `yaml:"analytics,omitempty"`
}

type MarketSource struct {
	Provider string   `yaml:"provider"`
	Indices  []string `yaml:"indices"`
}

type AnalyticsSource struct {
	StdPeriod       []int   `yaml:"std_period"`
	BollingerPeriod int     `yaml:"bollinger_period"`
	ZScoreThreshold float64 `yaml:"zscore_threshold"`
}

type AffiliateConfig struct {
	Programs   []AffiliateProgram `yaml:"programs"`
	Disclosure string             `yaml:"disclosure"`
	Placement  string             `yaml:"placement,omitempty"`
}

type AffiliateProgram struct {
	Name       string   `yaml:"name"`
	ID         string   `yaml:"id"`
	Categories []string `yaml:"categories"`
}

// Site represents a fully loaded site with both config and agent settings.
type Site struct {
	Name      string
	Path      string      // filesystem path to sites/{name}/
	Config    SiteConfig
	Agent     AgentConfig
	LoadedAt  time.Time
}
