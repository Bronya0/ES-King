/*
 * Copyright 2025 Bronya0 <tangssst@163.com>.
 * Author Github: https://github.com/Bronya0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package service

import (
	"app/backend/types"
	"bufio"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/go-resty/resty/v2"
)

const (
	FORMAT          = "?format=json&pretty"
	StatsApi        = "/_cluster/stats" + FORMAT
	AddDoc          = "/_doc"
	HealthApi       = "/_cluster/health"
	NodesApi        = "/_nodes/stats/indices,os,fs,process,jvm"
	AllIndexApi     = "/_cat/indices?format=json&pretty&bytes=b"
	ClusterSettings = "/_cluster/settings"
	ForceMerge      = "/_forcemerge?wait_for_completion=false"
	REFRESH         = "/_refresh"
	FLUSH           = "/_flush"
	CacheClear      = "/_cache/clear"
	TasksApi        = "/_tasks" + FORMAT
	CancelTasksApi  = "/_tasks/%s/_cancel"
)

type ESService struct {
	ConnectObj *types.Connect
	Client     *resty.Client
	mu         sync.RWMutex
}

func NewESService() *ESService {
	return &ESService{
		Client:     newESClient(),
		ConnectObj: &types.Connect{},
	}
}

func ConfigureSSL(UseSSL, SkipSSLVerify bool, client *resty.Client, CACert string) {
	// Configure SSL
	// CACert是证书内容
	if UseSSL {
		client.SetScheme("https")
		if SkipSSLVerify {
			client.SetTLSClientConfig(&tls.Config{InsecureSkipVerify: true})
		}
		if CACert != "" {
			client.SetRootCertificateFromString(CACert)
		}
	} else {
		client.SetScheme("http")
	}
}

func newESClient() *resty.Client {
	client := resty.New()
	client.SetTimeout(30 * time.Second)
	client.SetRetryCount(0)
	client.SetHeader("Content-Type", "application/json")
	return client
}

func (es *ESService) SetConnect(key, host, username, password, CACert string, UseSSL, SkipSSLVerify bool) {
	es.mu.Lock()         // 加写锁
	defer es.mu.Unlock() // 方法结束时解锁

	es.ConnectObj = &types.Connect{
		Name:          key,
		Host:          host,
		Username:      username,
		Password:      password,
		UseSSL:        UseSSL,
		SkipSSLVerify: SkipSSLVerify,
		CACert:        CACert,
	}
	// 每次切换连接都重建 client，避免上一个集群的 BasicAuth、
	// InsecureSkipVerify、CA 证书等配置残留到新连接
	client := newESClient()
	if username != "" && password != "" {
		client.SetBasicAuth(username, password)
	}
	ConfigureSSL(UseSSL, SkipSSLVerify, client, CACert)
	es.Client = client

	fmt.Println("设置当前连接：", es.ConnectObj.Host)
}

func (es *ESService) TestClient(host, username, password, CACert string, UseSSL, SkipSSLVerify bool) string {
	client := newESClient()
	// 测试连接单独设置较短超时，避免连不上的主机长时间阻塞界面
	client.SetTimeout(10 * time.Second)
	if username != "" && password != "" {
		client.SetBasicAuth(username, password)
	}
	// Configure SSL
	ConfigureSSL(UseSSL, SkipSSLVerify, client, CACert)

	resp, err := client.R().Get(host + HealthApi)
	if err != nil {
		return err.Error()
	}
	if resp.StatusCode() != http.StatusOK {
		return string(resp.Body())
	}
	return ""
}

// AddDocument 添加文档
func (es *ESService) AddDocument(index, doc string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(doc).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/" + index + AddDoc)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusCreated {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetNodes() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + NodesApi)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetHealth() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + HealthApi)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetStats() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + StatsApi)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}

	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexes(name string) *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个集群"}
	}
	newUrl := es.ConnectObj.Host + AllIndexApi
	if name != "" {
		// 搜索词需要转义，避免空格、& 等字符破坏 URL，通配符 * 保持字面量
		newUrl += "&index=*" + url.QueryEscape(name) + "*"
	}
	log.Println(newUrl)
	var result []any

	resp, err := es.Client.R().SetResult(&result).Get(newUrl)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}

	return &types.ResultsResp{Results: result}

}

func (es *ESService) CreateIndex(name string, numberOfShards, numberOfReplicas int, mapping string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	indexConfig := types.H{
		"settings": types.H{
			"number_of_shards":   numberOfShards,
			"number_of_replicas": numberOfReplicas,
		},
	}
	if mapping != "" {
		var mappings types.H
		err := json.Unmarshal([]byte(mapping), &mappings)
		if err != nil {
			return &types.ResultResp{Err: err.Error()}
		}
		indexConfig["mappings"] = mappings
	}

	resp, err := es.Client.R().
		SetBody(indexConfig).
		Put(es.ConnectObj.Host + "/" + name)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{}

}

func (es *ESService) GetIndexInfo(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) DeleteIndex(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any
	resp, err := es.Client.R().SetResult(&result).Delete(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) OpenCloseIndex(indexName, now string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any
	action, ok := map[string]string{
		"open":  "_close",
		"close": "_open",
	}[now]
	if !ok {
		return &types.ResultResp{Err: "无效的状态参数: " + now}
	}
	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + "/" + action)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) GetIndexMappings(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) MergeSegments(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + ForceMerge)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) Refresh(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + REFRESH)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) Flush(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + FLUSH)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) CacheClear(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + CacheClear)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetDoc10(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}

	body := map[string]any{
		"query": map[string]any{
			"query_string": map[string]any{
				"query": "*",
			},
		},
		"size": 10,
		"from": 0,
		"sort": []any{},
	}
	var result map[string]any

	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/" + indexName + "/_search")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) Search(method, path string, body any) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result any

	req := es.Client.R().SetResult(&result)
	if body != nil {
		req = req.SetBody(body)
	}
	resp, err := req.Execute(method, es.ConnectObj.Host+path)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	// REST 控制台会常见 201 Created、202 Accepted 等成功状态码，统一放行 2xx
	if !resp.IsSuccess() {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	// 若返回内容非 JSON（如纯文本输出），SetResult 不会赋值 result，返回原始响应文本
	if result == nil && len(resp.Body()) > 0 {
		return &types.ResultResp{Result: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetClusterSettings() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + ClusterSettings)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexSettings(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexAliases(indexNameList []string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	indexNames := strings.Join(indexNameList, ",")
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexNames + "/_alias")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	alias := make(map[string]any)
	for name, obj := range result {
		if aliases, ok := obj.(map[string]any)["aliases"]; ok {
			names := make([]string, 0)
			aliases, ok := aliases.(map[string]any)
			if !ok {
				continue
			}
			for aliasName := range aliases {
				names = append(names, aliasName)
			}
			if len(names) > 0 {
				alias[name] = strings.Join(names, ",")
			}
		}
	}
	return &types.ResultResp{Result: alias}
}

func (es *ESService) GetIndexSegments(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetTasks() *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个集群"}
	}
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + TasksApi)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	nodes, ok := result["nodes"].(map[string]any)
	if !ok {
		return &types.ResultsResp{Err: "获取任务列表失败"}
	}

	var data []any
	for _, nodeObj := range nodes {
		nodeTasks, ok := nodeObj.(map[string]any)["tasks"].(map[string]any)
		if !ok {
			continue
		}
		for taskID, taskInfo := range nodeTasks {
			taskInfoMap, ok := taskInfo.(map[string]any)
			if !ok {
				continue
			}
			nodeName, ok := nodeObj.(map[string]any)
			if !ok {
				continue
			}
			nodeIp, ok := nodeObj.(map[string]any)
			if !ok {
				continue
			}
			data = append(data, map[string]any{
				"task_id":               taskID,
				"node_name":             nodeName["name"],
				"node_ip":               nodeIp["ip"],
				"type":                  taskInfoMap["type"],
				"action":                taskInfoMap["action"],
				"start_time_in_millis":  taskInfoMap["start_time_in_millis"],
				"running_time_in_nanos": taskInfoMap["running_time_in_nanos"],
				"cancellable":           taskInfoMap["cancellable"],
				"parent_task_id":        taskInfoMap["parent_task_id"],
			})
		}
	}
	return &types.ResultsResp{Results: data}
}

func (es *ESService) CancelTasks(taskID string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}

	newUrl := fmt.Sprintf(es.ConnectObj.Host+CancelTasksApi, url.PathEscape(taskID))
	var result map[string]any

	resp, err := es.Client.R().SetResult(&result).Post(newUrl)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// GetSnapshots 获取ES快照列表
func (es *ESService) GetSnapshots() *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个集群"}
	}

	// 1. 首先获取所有仓库列表
	var repositories map[string]interface{} // 修改目标类型
	reposResp, err := es.Client.R().Get(es.ConnectObj.Host + "/_snapshot")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if reposResp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(reposResp.Body())}
	}
	err = json.Unmarshal(reposResp.Body(), &repositories) // 直接解析到 map
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}

	// 2. 并发遍历每个仓库获取其快照
	var (
		mu           sync.Mutex
		allSnapshots []any
		wg           sync.WaitGroup
	)
	for repoName := range repositories {
		wg.Add(1)
		go func(repo string) {
			defer wg.Done()
			var repoResult map[string]interface{}
			resp, err := es.Client.R().SetResult(&repoResult).Get(es.ConnectObj.Host + "/_snapshot/" + repo + "/_all")
			if err != nil || resp.StatusCode() != http.StatusOK {
				return
			}

			// 3. 处理每个快照的数据（带安全类型断言）
			snapshots, ok := repoResult["snapshots"].([]interface{})
			if !ok {
				return
			}
			var items []any
			for _, snap := range snapshots {
				snapshot, ok := snap.(map[string]interface{})
				if !ok {
					continue
				}
				state, _ := snapshot["state"].(string)
				shards, _ := snapshot["shards"].(map[string]interface{})
				items = append(items, map[string]interface{}{
					"snapshot":          snapshot["snapshot"],
					"repository":        repo,
					"state":             strings.ToUpper(state),
					"start_time":        snapshot["start_time"],
					"end_time":          snapshot["end_time"],
					"indices":           snapshot["indices"],
					"total_shards":      shards["total"],
					"successful_shards": shards["successful"],
				})
			}
			mu.Lock()
			allSnapshots = append(allSnapshots, items...)
			mu.Unlock()
		}(repoName)
	}
	wg.Wait()

	return &types.ResultsResp{Results: allSnapshots}
}

// GetSnapshotRepositories 获取所有快照仓库
func (es *ESService) GetSnapshotRepositories() *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个集群"}
	}

	var repositories map[string]any
	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/_snapshot")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	err = json.Unmarshal(resp.Body(), &repositories)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}

	var data []any
	for name, info := range repositories {
		repoInfo, ok := info.(map[string]any)
		if !ok {
			continue
		}
		item := map[string]any{
			"name":     name,
			"type":     repoInfo["type"],
			"settings": repoInfo["settings"],
		}
		data = append(data, item)
	}
	return &types.ResultsResp{Results: data}
}

// CreateSnapshotRepository 创建快照仓库
func (es *ESService) CreateSnapshotRepository(name, repoType, settings string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if name == "" || repoType == "" {
		return &types.ResultResp{Err: "仓库名称和类型不能为空"}
	}

	var settingsMap map[string]any
	if settings != "" {
		if err := json.Unmarshal([]byte(settings), &settingsMap); err != nil {
			return &types.ResultResp{Err: "settings JSON 格式无效: " + err.Error()}
		}
	}

	body := map[string]any{
		"type":     repoType,
		"settings": settingsMap,
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/_snapshot/" + url.PathEscape(name))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// DeleteSnapshotRepository 删除快照仓库
func (es *ESService) DeleteSnapshotRepository(name string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if name == "" {
		return &types.ResultResp{Err: "仓库名称不能为空"}
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Delete(es.ConnectObj.Host + "/_snapshot/" + url.PathEscape(name))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// VerifySnapshotRepository 验证快照仓库
func (es *ESService) VerifySnapshotRepository(name string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if name == "" {
		return &types.ResultResp{Err: "仓库名称不能为空"}
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_snapshot/" + url.PathEscape(name) + "/_verify")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// CreateSnapshot 创建快照（异步）
func (es *ESService) CreateSnapshot(repository, snapshot, indices string, includeGlobalState bool) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if repository == "" || snapshot == "" {
		return &types.ResultResp{Err: "仓库名称和快照名称不能为空"}
	}

	body := map[string]any{
		"include_global_state": includeGlobalState,
	}
	if indices != "" {
		body["indices"] = indices
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/_snapshot/" + url.PathEscape(repository) + "/" + url.PathEscape(snapshot) + "?wait_for_completion=false")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK && resp.StatusCode() != http.StatusAccepted {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// DeleteSnapshot 删除快照
func (es *ESService) DeleteSnapshot(repository, snapshot string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if repository == "" || snapshot == "" {
		return &types.ResultResp{Err: "仓库名称和快照名称不能为空"}
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Delete(es.ConnectObj.Host + "/_snapshot/" + url.PathEscape(repository) + "/" + url.PathEscape(snapshot))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// GetSnapshotDetail 获取快照详情
func (es *ESService) GetSnapshotDetail(repository, snapshot string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if repository == "" || snapshot == "" {
		return &types.ResultResp{Err: "仓库名称和快照名称不能为空"}
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Get(es.ConnectObj.Host + "/_snapshot/" + url.PathEscape(repository) + "/" + url.PathEscape(snapshot))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// RestoreSnapshot 恢复快照（异步）
func (es *ESService) RestoreSnapshot(repository, snapshot, indices, renamePattern, renameReplacement string, includeGlobalState bool) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if repository == "" || snapshot == "" {
		return &types.ResultResp{Err: "仓库名称和快照名称不能为空"}
	}

	body := map[string]any{
		"include_global_state": includeGlobalState,
	}
	if indices != "" {
		body["indices"] = indices
	}
	if renamePattern != "" {
		body["rename_pattern"] = renamePattern
	}
	if renameReplacement != "" {
		body["rename_replacement"] = renameReplacement
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_snapshot/" + url.PathEscape(repository) + "/" + url.PathEscape(snapshot) + "/_restore?wait_for_completion=false")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK && resp.StatusCode() != http.StatusAccepted {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// GetSnapshotRestoreStatus 获取快照恢复状态
func (es *ESService) GetSnapshotRestoreStatus() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Get(es.ConnectObj.Host + "/_recovery?active_only=true&format=json")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// GetSLMPolicies 获取所有SLM策略
func (es *ESService) GetSLMPolicies() *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个集群"}
	}

	var result []any
	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/_slm/policy")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	// SLM API 返回的是一个对象 {policyId: {...}, ...}
	var policiesMap map[string]any
	if err := json.Unmarshal(resp.Body(), &policiesMap); err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}

	for name, info := range policiesMap {
		policyInfo, ok := info.(map[string]any)
		if !ok {
			continue
		}
		policyInfo["name"] = name
		result = append(result, policyInfo)
	}
	return &types.ResultsResp{Results: result}
}

// CreateSLMPolicy 创建SLM策略
func (es *ESService) CreateSLMPolicy(policyId, name, schedule, repository, indices, expireAfter string, minCount, maxCount int) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if policyId == "" || schedule == "" || repository == "" {
		return &types.ResultResp{Err: "策略ID、调度计划和仓库名称不能为空"}
	}

	body := map[string]any{
		"schedule":   schedule,
		"name":       name,
		"repository": repository,
		"config": map[string]any{
			"indices":              []string{"*"},
			"include_global_state": false,
		},
	}
	if indices != "" {
		body["config"].(map[string]any)["indices"] = strings.Split(indices, ",")
	}

	retention := map[string]any{}
	if expireAfter != "" {
		retention["expire_after"] = expireAfter
	}
	if minCount > 0 {
		retention["min_count"] = minCount
	}
	if maxCount > 0 {
		retention["max_count"] = maxCount
	}
	if len(retention) > 0 {
		body["retention"] = retention
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/_slm/policy/" + url.PathEscape(policyId))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// DeleteSLMPolicy 删除SLM策略
func (es *ESService) DeleteSLMPolicy(policyId string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if policyId == "" {
		return &types.ResultResp{Err: "策略ID不能为空"}
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Delete(es.ConnectObj.Host + "/_slm/policy/" + url.PathEscape(policyId))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// ExecuteSLMPolicy 手动执行SLM策略
func (es *ESService) ExecuteSLMPolicy(policyId string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	if policyId == "" {
		return &types.ResultResp{Err: "策略ID不能为空"}
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_slm/policy/" + url.PathEscape(policyId) + "/_execute")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// SearchResponse 定义 ES 搜索响应的结构
type SearchResponse struct {
	ScrollID string `json:"_scroll_id"`
	Hits     struct {
		Total struct {
			Value int `json:"value"`
		} `json:"total"`
		Hits []struct {
			Source json.RawMessage `json:"_source"`
		} `json:"hits"`
	} `json:"hits"`
}

// DownloadESIndex 使用 Resty 客户端从 ES 下载指定索引的数据
func (es *ESService) DownloadESIndex(index string, queryDSL string, filePath string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}

	res := &types.ResultResp{}
	// 如果 queryDSL 为空，默认使用 match_all 查询
	if queryDSL == "" {
		queryDSL = `{"match_all": {}}`
	}

	// 前端传来的路径以 / 或 \ 开头，在各操作系统下会解析到系统根目录（通常无写权限），统一落到用户主目录
	if strings.HasPrefix(filePath, "/") || strings.HasPrefix(filePath, "\\") {
		rel := strings.TrimLeft(filePath, "/\\")
		if home, err := os.UserHomeDir(); err == nil {
			filePath = filepath.Join(home, rel)
		}
	}

	// 创建本地文件
	file, err := os.Create(filePath)
	if err != nil {
		res.Err = fmt.Sprintf("创建文件失败: %v", err)
		return res
	}
	success := false
	defer func() {
		file.Close()
		if !success {
			os.Remove(filePath) // 下载失败时清理残缺文件
		}
	}()

	// 构造初始搜索请求的 body，设置每批次大小为 10000
	bodyStr := fmt.Sprintf(`{"size": 10000, "query": %s}`, queryDSL)
	resp, err := es.Client.R().SetBody(bodyStr).Post(es.ConnectObj.Host + "/" + index + "/_search?scroll=3m")
	if err != nil {
		res.Err = fmt.Sprintf("初始搜索请求失败: %v", err)
		return res
	}
	if resp.StatusCode() != 200 {
		res.Err = "初始搜索请求返回非 200 状态码"
		return res
	}

	// 解析初始响应
	var searchResponse SearchResponse
	err = json.Unmarshal(resp.Body(), &searchResponse)
	if err != nil {
		res.Err = fmt.Sprintf("解析初始响应失败: %v", err)
		return res
	}

	// 使用 bufio.Writer 进行缓冲写入
	writer := bufio.NewWriter(file)
	defer writer.Flush() // 确保缓冲区数据在函数结束时写入文件

	// 写入 JSON 数组的开头
	_, _ = writer.WriteString("[")

	// 标志变量，用于控制逗号分隔符
	isFirst := true

	// 循环处理滚动下载
	for {
		// 如果当前批次没有文档，则退出循环
		if len(searchResponse.Hits.Hits) == 0 {
			break
		}

		// 遍历当前批次的每个文档
		for _, hit := range searchResponse.Hits.Hits {
			if !isFirst {
				// 除了第一个文档前，其他文档前添加逗号
				_, _ = writer.WriteString(",")
			}
			isFirst = false
			// 直接写入文档的 _source 字段（json.RawMessage 是 []byte 类型）
			_, _ = writer.Write(hit.Source)
		}

		// 发送滚动请求获取下一批数据
		scrollBody := map[string]interface{}{
			"scroll":    "3m", // 滚动上下文有效期 1 分钟
			"scroll_id": searchResponse.ScrollID,
		}
		resp, err = es.Client.R().SetBody(scrollBody).Post(es.ConnectObj.Host + "/_search/scroll")
		if err != nil {
			res.Err = fmt.Sprintf("滚动请求失败: %v", err)
			return res
		}
		if resp.StatusCode() != 200 {
			res.Err = fmt.Sprintf("滚动请求返回非 200 状态码 %v", resp.StatusCode())
			return res
		}

		// 解析滚动响应
		err = json.Unmarshal(resp.Body(), &searchResponse)
		if err != nil {
			res.Err = fmt.Sprintf("解析滚动响应失败: %v", err)
			return res
		}
	}

	// 写入 JSON 数组的结尾
	_, _ = writer.WriteString("]")

	// 主动清理滚动上下文，不占用 ES 的 scroll 资源等待超时
	if searchResponse.ScrollID != "" {
		_, _ = es.Client.R().
			SetBody(map[string]any{"scroll_id": []string{searchResponse.ScrollID}}).
			Delete(es.ConnectObj.Host + "/_search/scroll")
	}

	success = true
	res.Result = filePath
	return res
}

// ==================== 文档管理 ====================

func (es *ESService) checkConnect() string {
	if es.ConnectObj.Host == "" {
		return "请先选择一个集群"
	}
	return ""
}

// SearchDocs 分页查询文档，query 为查询子句 JSON（如 {"term":{"a":1}}），也可传整个 {"query":{...}} 会自动解包
func (es *ESService) SearchDocs(indexName, query string, from, size int) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	body := types.H{
		"from":             from,
		"size":             size,
		"track_total_hits": true,
	}
	if query != "" {
		var q any
		if err := json.Unmarshal([]byte(query), &q); err != nil {
			return &types.ResultResp{Err: "查询DSL不是合法的JSON: " + err.Error()}
		}
		if m, ok := q.(map[string]any); ok {
			if inner, ok := m["query"]; ok {
				body["query"] = inner
			} else {
				body["query"] = m
			}
		}
	} else {
		body["query"] = types.H{"match_all": types.H{}}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/" + indexName + "/_search")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// GetDoc 获取单个文档
func (es *ESService) GetDoc(indexName, docID string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Get(es.ConnectObj.Host + "/" + indexName + "/_doc/" + url.PathEscape(docID))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// UpdateDoc 覆盖更新单个文档
func (es *ESService) UpdateDoc(indexName, docID, doc string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if !json.Valid([]byte(doc)) {
		return &types.ResultResp{Err: "文档内容不是合法的JSON"}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(doc).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/" + indexName + "/_doc/" + url.PathEscape(docID))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK && resp.StatusCode() != http.StatusCreated {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// DeleteDoc 删除单个文档
func (es *ESService) DeleteDoc(indexName, docID string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Delete(es.ConnectObj.Host + "/" + indexName + "/_doc/" + url.PathEscape(docID))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// DeleteByQuery 按查询删除文档，query 为查询子句 JSON
func (es *ESService) DeleteByQuery(indexName, query string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if query == "" {
		return &types.ResultResp{Err: "按查询删除必须提供查询条件，禁止全量删除"}
	}
	var q any
	if err := json.Unmarshal([]byte(query), &q); err != nil {
		return &types.ResultResp{Err: "查询DSL不是合法的JSON: " + err.Error()}
	}
	if m, ok := q.(map[string]any); ok {
		if inner, ok := m["query"]; ok {
			q = inner
		}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(types.H{"query": q}).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/" + indexName + "/_delete_by_query?wait_for_completion=false")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK && resp.StatusCode() != http.StatusAccepted {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// BulkImport 批量导入文档，docs 为 JSON 数组字符串
func (es *ESService) BulkImport(indexName, docs string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	var arr []any
	if err := json.Unmarshal([]byte(docs), &arr); err != nil {
		return &types.ResultResp{Err: "文档数据必须是JSON数组: " + err.Error()}
	}
	if len(arr) == 0 {
		return &types.ResultResp{Err: "没有可导入的文档"}
	}

	var ndjson strings.Builder
	for _, doc := range arr {
		meta, _ := json.Marshal(types.H{"index": types.H{"_index": indexName}})
		docBytes, err := json.Marshal(doc)
		if err != nil {
			return &types.ResultResp{Err: "文档序列化失败: " + err.Error()}
		}
		ndjson.Write(meta)
		ndjson.WriteByte('\n')
		ndjson.Write(docBytes)
		ndjson.WriteByte('\n')
	}

	var result map[string]any
	resp, err := es.Client.R().
		SetBody(ndjson.String()).
		SetHeader("Content-Type", "application/x-ndjson").
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_bulk")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}

	failed := 0
	firstErr := ""
	if items, ok := result["items"].([]any); ok {
		for _, item := range items {
			itemMap, ok := item.(map[string]any)
			if !ok {
				continue
			}
			for _, op := range itemMap {
				opMap, ok := op.(map[string]any)
				if !ok {
					continue
				}
				if status, ok := opMap["status"].(float64); ok && status >= 400 {
					failed++
					if firstErr == "" {
						errBytes, _ := json.Marshal(opMap["error"])
						firstErr = string(errBytes)
					}
				}
			}
		}
	}
	summary := types.H{
		"total":   len(arr),
		"success": len(arr) - failed,
		"failed":  failed,
	}
	if firstErr != "" {
		summary["first_error"] = firstErr
	}
	return &types.ResultResp{Result: summary}
}

// GetFieldTopValues 字段Top值统计与基数
func (es *ESService) GetFieldTopValues(indexName, field string, size int) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if field == "" {
		return &types.ResultResp{Err: "请输入字段名"}
	}
	if size <= 0 {
		size = 10
	}
	body := types.H{
		"size": 0,
		"aggs": types.H{
			"top_values": types.H{
				"terms": types.H{"field": field, "size": size},
			},
			"unique_count": types.H{
				"cardinality": types.H{"field": field},
			},
		},
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/" + indexName + "/_search")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// ==================== 别名管理 ====================

// AddIndexAlias 为索引添加别名，extra 为可选的 filter/routing 等 JSON
func (es *ESService) AddIndexAlias(indexName, alias, extra string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if indexName == "" || alias == "" {
		return &types.ResultResp{Err: "索引名和别名不能为空"}
	}
	action := types.H{
		"index": indexName,
		"alias": alias,
	}
	if extra != "" {
		var extraMap map[string]any
		if err := json.Unmarshal([]byte(extra), &extraMap); err != nil {
			return &types.ResultResp{Err: "别名参数不是合法的JSON: " + err.Error()}
		}
		for k, v := range extraMap {
			action[k] = v
		}
	}
	body := types.H{"actions": []any{types.H{"add": action}}}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_aliases")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// RemoveIndexAlias 移除索引别名
func (es *ESService) RemoveIndexAlias(indexName, alias string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if indexName == "" || alias == "" {
		return &types.ResultResp{Err: "索引名和别名不能为空"}
	}
	body := types.H{"actions": []any{types.H{"remove": types.H{
		"index": indexName,
		"alias": alias,
	}}}}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_aliases")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// ==================== Reindex ====================

// Reindex 从源索引复制数据到目标索引（异步），query 为可选的查询子句 JSON
func (es *ESService) Reindex(source, dest, query string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if source == "" || dest == "" {
		return &types.ResultResp{Err: "源索引和目标索引不能为空"}
	}
	sourceBody := types.H{"index": source}
	if query != "" {
		var q any
		if err := json.Unmarshal([]byte(query), &q); err != nil {
			return &types.ResultResp{Err: "查询DSL不是合法的JSON: " + err.Error()}
		}
		if m, ok := q.(map[string]any); ok {
			if inner, ok := m["query"]; ok {
				q = inner
			}
		}
		sourceBody["query"] = q
	}
	body := types.H{
		"source": sourceBody,
		"dest":   types.H{"index": dest},
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_reindex?wait_for_completion=false")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK && resp.StatusCode() != http.StatusAccepted {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// ==================== Mapping / Settings 编辑 ====================

// UpdateIndexMappings 更新索引 mapping（只能新增字段，不能修改已有字段类型）
func (es *ESService) UpdateIndexMappings(indexName, mapping string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if !json.Valid([]byte(mapping)) {
		return &types.ResultResp{Err: "mapping不是合法的JSON"}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(mapping).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/" + indexName + "/_mapping")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// UpdateIndexSettings 更新索引动态设置
func (es *ESService) UpdateIndexSettings(indexName, settings string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if !json.Valid([]byte(settings)) {
		return &types.ResultResp{Err: "settings不是合法的JSON"}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(settings).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/" + indexName + "/_settings")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// ==================== ILM 索引生命周期管理 ====================

// GetILMPolicies 获取所有ILM策略
func (es *ESService) GetILMPolicies() *types.ResultsResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultsResp{Err: msg}
	}
	var policiesMap map[string]any
	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/_ilm/policy")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	if err := json.Unmarshal(resp.Body(), &policiesMap); err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	var result []any
	for name, info := range policiesMap {
		infoMap, ok := info.(map[string]any)
		if !ok {
			continue
		}
		infoMap["name"] = name
		result = append(result, infoMap)
	}
	return &types.ResultsResp{Results: result}
}

// CreateILMPolicy 创建或更新ILM策略，policy 为完整的策略 JSON（含 phases）
func (es *ESService) CreateILMPolicy(policyId, policy string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if policyId == "" || policy == "" {
		return &types.ResultResp{Err: "策略ID和策略内容不能为空"}
	}
	var body any
	if err := json.Unmarshal([]byte(policy), &body); err != nil {
		return &types.ResultResp{Err: "策略内容不是合法的JSON: " + err.Error()}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/_ilm/policy/" + url.PathEscape(policyId))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// DeleteILMPolicy 删除ILM策略
func (es *ESService) DeleteILMPolicy(policyId string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if policyId == "" {
		return &types.ResultResp{Err: "策略ID不能为空"}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Delete(es.ConnectObj.Host + "/_ilm/policy/" + url.PathEscape(policyId))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// ==================== 索引模板 ====================

// GetIndexTemplates 获取所有索引模板（支持 ES 7.8+ _index_template 与旧版本 _template）
func (es *ESService) GetIndexTemplates() *types.ResultsResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultsResp{Err: msg}
	}
	var result map[string]any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/_index_template")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		// 旧版 ES (<7.8) 不支持 _index_template，回退至 legacy _template
		if strings.Contains(string(resp.Body()), "invalid_index_name_exception") {
			var legacyResult map[string]any
			legacyResp, lErr := es.Client.R().SetResult(&legacyResult).Get(es.ConnectObj.Host + "/_template")
			if lErr != nil {
				return &types.ResultsResp{Err: lErr.Error()}
			}
			if legacyResp.StatusCode() != http.StatusOK {
				return &types.ResultsResp{Err: string(legacyResp.Body())}
			}
			var data []any
			for name, tpl := range legacyResult {
				tplMap, ok := tpl.(map[string]any)
				if !ok {
					continue
				}
				item := map[string]any{
					"name":           name,
					"index_patterns": tplMap["index_patterns"],
					"priority":       tplMap["order"],
					"version":        tplMap["version"],
					"_template": map[string]any{
						"settings": tplMap["settings"],
						"mappings": tplMap["mappings"],
						"aliases":  tplMap["aliases"],
					},
				}
				data = append(data, item)
			}
			return &types.ResultsResp{Results: data}
		}
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	var data []any
	if templates, ok := result["index_templates"].([]any); ok {
		for _, tpl := range templates {
			tplMap, ok := tpl.(map[string]any)
			if !ok {
				continue
			}
			item := map[string]any{"name": tplMap["name"]}
			if body, ok := tplMap["index_template"].(map[string]any); ok {
				item["index_patterns"] = body["index_patterns"]
				item["composed_of"] = body["composed_of"]
				item["priority"] = body["priority"]
				item["version"] = body["version"]
				item["_template"] = body["template"]
			}
			data = append(data, item)
		}
	}
	return &types.ResultsResp{Results: data}
}

// CreateIndexTemplate 创建或更新索引模板，body 为完整模板 JSON
func (es *ESService) CreateIndexTemplate(name, body string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if name == "" || body == "" {
		return &types.ResultResp{Err: "模板名称和内容不能为空"}
	}
	var bodyAny any
	if err := json.Unmarshal([]byte(body), &bodyAny); err != nil {
		return &types.ResultResp{Err: "模板内容不是合法的JSON: " + err.Error()}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(bodyAny).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/_index_template/" + url.PathEscape(name))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		if strings.Contains(string(resp.Body()), "invalid_index_name_exception") {
			// 旧版本 ES (<7.8) 回退至 /_template/{name}
			resp, err = es.Client.R().
				SetBody(bodyAny).
				SetResult(&result).
				Put(es.ConnectObj.Host + "/_template/" + url.PathEscape(name))
			if err != nil {
				return &types.ResultResp{Err: err.Error()}
			}
			if resp.StatusCode() != http.StatusOK {
				return &types.ResultResp{Err: string(resp.Body())}
			}
			return &types.ResultResp{Result: result}
		}
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// DeleteIndexTemplate 删除索引模板
func (es *ESService) DeleteIndexTemplate(name string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if name == "" {
		return &types.ResultResp{Err: "模板名称不能为空"}
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetResult(&result).
		Delete(es.ConnectObj.Host + "/_index_template/" + url.PathEscape(name))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		if strings.Contains(string(resp.Body()), "invalid_index_name_exception") {
			// 旧版本 ES (<7.8) 回退至 /_template/{name}
			resp, err = es.Client.R().
				SetResult(&result).
				Delete(es.ConnectObj.Host + "/_template/" + url.PathEscape(name))
			if err != nil {
				return &types.ResultResp{Err: err.Error()}
			}
			if resp.StatusCode() != http.StatusOK {
				return &types.ResultResp{Err: string(resp.Body())}
			}
			return &types.ResultResp{Result: result}
		}
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// GetComponentTemplates 获取所有组件模板
func (es *ESService) GetComponentTemplates() *types.ResultsResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultsResp{Err: msg}
	}
	var result map[string]any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/_component_template")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		// 旧版 ES (<7.8) 无组件模板概念，返回空列表
		if strings.Contains(string(resp.Body()), "invalid_index_name_exception") {
			return &types.ResultsResp{Results: []any{}}
		}
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	var data []any
	if templates, ok := result["component_templates"].([]any); ok {
		for _, tpl := range templates {
			tplMap, ok := tpl.(map[string]any)
			if !ok {
				continue
			}
			item := map[string]any{"name": tplMap["name"]}
			if body, ok := tplMap["component_template"].(map[string]any); ok {
				item["version"] = body["version"]
				item["_template"] = body["template"]
			}
			data = append(data, item)
		}
	}
	return &types.ResultsResp{Results: data}
}

// CreateIndexFromTemplate 基于索引模板创建索引，合并模板中的 settings 和 mappings
func (es *ESService) CreateIndexFromTemplate(indexName, templateName string, numberOfShards, numberOfReplicas int) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if indexName == "" || templateName == "" {
		return &types.ResultResp{Err: "索引名和模板名不能为空"}
	}

	var tplResult map[string]any
	resp, err := es.Client.R().
		SetResult(&tplResult).
		Get(es.ConnectObj.Host + "/_index_template/" + url.PathEscape(templateName))
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		if strings.Contains(string(resp.Body()), "invalid_index_name_exception") {
			// 旧版 ES (<7.8) 回退至 /_template/{name}
			var legacyTpl map[string]any
			resp, err = es.Client.R().
				SetResult(&legacyTpl).
				Get(es.ConnectObj.Host + "/_template/" + url.PathEscape(templateName))
			if err != nil {
				return &types.ResultResp{Err: err.Error()}
			}
			if resp.StatusCode() != http.StatusOK {
				return &types.ResultResp{Err: string(resp.Body())}
			}
			if tplObj, ok := legacyTpl[templateName].(map[string]any); ok {
				body := types.H{}
				settings := types.H{
					"number_of_shards":   numberOfShards,
					"number_of_replicas": numberOfReplicas,
				}
				if s, ok := tplObj["settings"].(map[string]any); ok {
					for k, v := range s {
						settings[k] = v
					}
				}
				if m, ok := tplObj["mappings"]; ok && m != nil {
					body["mappings"] = m
				}
				body["settings"] = settings
				var createResult map[string]any
				resp, err = es.Client.R().
					SetBody(body).
					SetResult(&createResult).
					Put(es.ConnectObj.Host + "/" + indexName)
				if err != nil {
					return &types.ResultResp{Err: err.Error()}
				}
				if resp.StatusCode() != http.StatusOK {
					return &types.ResultResp{Err: string(resp.Body())}
				}
				return &types.ResultResp{Result: createResult}
			}
		}
		return &types.ResultResp{Err: string(resp.Body())}
	}

	body := types.H{}
	settings := types.H{
		"number_of_shards":   numberOfShards,
		"number_of_replicas": numberOfReplicas,
	}
	if templates, ok := tplResult["index_templates"].([]any); ok && len(templates) > 0 {
		if tplMap, ok := templates[0].(map[string]any); ok {
			if indexTemplate, ok := tplMap["index_template"].(map[string]any); ok {
				if tpl, ok := indexTemplate["template"].(map[string]any); ok {
					if s, ok := tpl["settings"].(map[string]any); ok {
						for k, v := range s {
							settings[k] = v
						}
					}
					if m, ok := tpl["mappings"]; ok && m != nil {
						body["mappings"] = m
					}
				}
			}
		}
	}
	body["settings"] = settings

	var result map[string]any
	resp, err = es.Client.R().
		SetBody(body).
		SetResult(&result).
		Put(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

// ==================== 分片与诊断 ====================

// GetShards 获取分片分布，index 为空时获取所有
func (es *ESService) GetShards(index string) *types.ResultsResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultsResp{Err: msg}
	}
	api := "/_cat/shards?format=json&bytes=b&h=index,shard,prirep,state,docs,store,ip,node"
	index = strings.TrimSpace(index)
	if index != "" {
		api = "/_cat/shards/" + index + "?format=json&bytes=b&h=index,shard,prirep,state,docs,store,ip,node"
	}
	var result []any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + api)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	return &types.ResultsResp{Results: result}
}

// ExplainAllocation 解释分片分配情况
func (es *ESService) ExplainAllocation(indexName string, shard int, primary bool) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if indexName == "" {
		return &types.ResultResp{Err: "索引名不能为空"}
	}
	body := types.H{
		"index":   indexName,
		"shard":   shard,
		"primary": primary,
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/_cluster/allocation/explain")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	// ES 对已分配的分片返回 400 并附解释信息，同样返回给前端展示
	if resp.StatusCode() != http.StatusOK && len(resp.Body()) == 0 {
		return &types.ResultResp{Err: fmt.Sprintf("HTTP %d", resp.StatusCode())}
	}
	if resp.StatusCode() == http.StatusOK {
		return &types.ResultResp{Result: result}
	}
	return &types.ResultResp{Err: string(resp.Body())}
}

// GetHotThreads 获取节点热点线程（文本），nodeId 为空时获取集群全部节点
func (es *ESService) GetHotThreads(nodeId string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	api := "/_nodes/hot_threads"
	nodeId = strings.TrimSpace(nodeId)
	if nodeId != "" {
		api = "/_nodes/" + url.PathEscape(nodeId) + "/hot_threads"
	}
	resp, err := es.Client.R().Get(es.ConnectObj.Host + api)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: string(resp.Body())}
}

// GetNodeNames 获取集群简要节点列表（用于下拉选择节点）
func (es *ESService) GetNodeNames() *types.ResultsResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultsResp{Err: msg}
	}
	var result []any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/_cat/nodes?format=json&h=name,ip,master,node.role")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	return &types.ResultsResp{Results: result}
}

// GetPendingTasks 获取集群挂起的任务
func (es *ESService) GetPendingTasks() *types.ResultsResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultsResp{Err: msg}
	}
	var result struct {
		Tasks []any `json:"tasks"`
	}
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/_cluster/pending_tasks")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	return &types.ResultsResp{Results: result.Tasks}
}

// GetThreadPool 获取线程池状态
func (es *ESService) GetThreadPool() *types.ResultsResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultsResp{Err: msg}
	}
	var result []any
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/_cat/thread_pool?format=json&pretty")
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	return &types.ResultsResp{Results: result}
}

// ==================== 分词调试 ====================

// AnalyzeText 分词调试，indexName 为空时使用集群默认分词
func (es *ESService) AnalyzeText(indexName, text, analyzer, field string) *types.ResultResp {
	if msg := es.checkConnect(); msg != "" {
		return &types.ResultResp{Err: msg}
	}
	if text == "" {
		return &types.ResultResp{Err: "请输入要分析的文本"}
	}
	body := types.H{"text": []string{text}}
	if field != "" {
		body["field"] = field
	} else if analyzer != "" {
		body["analyzer"] = analyzer
	}
	api := "/_analyze"
	if indexName != "" {
		api = "/" + indexName + api
	}
	var result map[string]any
	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + api)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != http.StatusOK {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}
