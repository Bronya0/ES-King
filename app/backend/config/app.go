package config

import (
	"app/backend/common"
	"app/backend/types"
	"context"
	"fmt"
	"gopkg.in/yaml.v3"
	"os"
	"path/filepath"
	"sync"
)

type AppConfig struct {
	ctx context.Context
	mu  sync.Mutex
}

func (a *AppConfig) Start(ctx context.Context) {
	a.ctx = ctx
}

func (a *AppConfig) GetConfig() *types.Config {
	configPath := a.getConfigPath()
	defaultConfig := &types.Config{
		Width:    common.Width,
		Height:   common.Height,
		Language: common.Language,
		Theme:    common.Theme,
		Connects: make([]types.Connect, 0),
	}
	data, err := os.ReadFile(configPath)
	if err != nil {
		return defaultConfig
	}
	err = yaml.Unmarshal(data, &defaultConfig)
	if err != nil {
		return defaultConfig
	}
	return defaultConfig
}

func (a *AppConfig) SaveConfig(config *types.Config) string {
	a.mu.Lock()
	defer a.mu.Unlock()
	configPath := a.getConfigPath()
	fmt.Println(configPath)

	data, err := yaml.Marshal(config)
	if err != nil {
		return err.Error()
	}

	err = os.WriteFile(configPath, data, 0644)
	if err != nil {
		return err.Error()
	}
	return ""
}
func (a *AppConfig) SaveTheme(theme string) string {
	config := a.GetConfig()
	config.Theme = theme
	data, err := yaml.Marshal(config)
	if err != nil {
		return err.Error()
	}
	configPath := a.getConfigPath()
	err = os.WriteFile(configPath, data, 0644)
	if err != nil {
		return err.Error()
	}
	return ""
}
func (a *AppConfig) getConfigPath() string {

	exePath, err := os.Executable()
	if err != nil {
		return common.ConfigPath
	}
	res, _ := filepath.EvalSymlinks(filepath.Dir(exePath))
	return filepath.Join(res, common.ConfigPath)

}

// GetVersion returns the application version
func (a *AppConfig) GetVersion() string {
	return common.Version
}

func (a *AppConfig) GetAppName() string {
	return common.AppName
}
