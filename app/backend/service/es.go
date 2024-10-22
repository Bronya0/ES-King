package service

import (
	"app/backend/types"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"fmt"
	"log"
	"net/url"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
)

const (
	FORMAT          = "?format=json&pretty"
	StatsApi        = "/_cluster/stats" + FORMAT
	HealthApi       = "/_cluster/health"
	NodesApi        = "/_cat/nodes?format=json&pretty&h=ip,name,heap.percent,heap.current,heap.max,ram.percent,ram.current,ram.max,node.role,master,cpu,load_5m,disk.used_percent,disk.used,disk.total,fielddataMemory,queryCacheMemory,requestCacheMemory,segmentsMemory,segments.count"
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
}

func NewESService() *ESService {
	client := resty.New()
	client.SetTimeout(30 * time.Second)
	client.SetRetryCount(0)
	client.SetHeader("Content-Type", "application/json")
	return &ESService{
		Client:     client,
		ConnectObj: &types.Connect{},
	}
}

func ConfigureSSL(UseSSL, SkipSSLVerify bool, client *resty.Client, CACert string) {
	// Configure SSL
	if UseSSL {
		client.SetScheme("https")
		if SkipSSLVerify {
			client.SetTLSClientConfig(&tls.Config{InsecureSkipVerify: true})
		}
		if CACert != "" {
			caCertPool := x509.NewCertPool()
			caCertPool.AppendCertsFromPEM([]byte(CACert))
			client.SetRootCertificate(CACert)
		}
	} else {
		client.SetScheme("http")
	}
}

func (es *ESService) SetConnect(key, host, username, password, CACert string, UseSSL, SkipSSLVerify bool) {
	es.ConnectObj = &types.Connect{
		Name:          key,
		Host:          host,
		Username:      username,
		Password:      password,
		UseSSL:        UseSSL,
		SkipSSLVerify: SkipSSLVerify,
		CACert:        CACert,
	}
	if username != "" && password != "" {
		es.Client.SetBasicAuth(username, password)
	}
	ConfigureSSL(UseSSL, SkipSSLVerify, es.Client, CACert)

	fmt.Println("设置当前连接：", es.ConnectObj.Host)
}

func (es *ESService) TestClient(host, username, password, CACert string, UseSSL, SkipSSLVerify bool) string {
	client := resty.New()
	if username != "" && password != "" {
		client.SetBasicAuth(username, password)
	}
	// Configure SSL
	ConfigureSSL(UseSSL, SkipSSLVerify, client, CACert)

	resp, err := client.R().Get(host + HealthApi)
	if err != nil {
		return err.Error()
	}
	if resp.StatusCode() != 200 {
		return string(resp.Body())
	}
	return ""
}

func (es *ESService) GetNodes() *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个集群"}
	}
	var result []interface{}
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + NodesApi)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	return &types.ResultsResp{Results: result}
}

func (es *ESService) GetHealth() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + HealthApi)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetStats() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + StatsApi)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}

	if resp.StatusCode() != 200 {
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
		newUrl += "&index=" + "*" + name + "*"
	}
	log.Println(newUrl)
	var result []interface{}

	resp, err := es.Client.R().SetResult(&result).Get(newUrl)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
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
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{}

}

func (es *ESService) GetIndexInfo(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) DeleteIndex(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}
	resp, err := es.Client.R().SetResult(&result).Delete(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) OpenCloseIndex(indexName, now string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}
	action := map[string]string{
		"open":  "_close",
		"close": "_open",
	}[now]
	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + "/" + action)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) GetIndexMappings(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) MergeSegments(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + ForceMerge)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) Refresh(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + REFRESH)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) Flush(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + FLUSH)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) CacheClear(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Post(es.ConnectObj.Host + "/" + indexName + CacheClear)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetDoc10(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}

	body := map[string]interface{}{
		"query": map[string]interface{}{
			"query_string": map[string]interface{}{
				"query": "*",
			},
		},
		"size": 10,
		"from": 0,
		"sort": []interface{}{},
	}
	var result map[string]interface{}

	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Post(es.ConnectObj.Host + "/" + indexName + "/_search")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) Search(method, path string, body interface{}) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().
		SetBody(body).
		SetResult(&result).
		Execute(method, es.ConnectObj.Host+path)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetClusterSettings() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + ClusterSettings)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexSettings(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexAliases(indexNameList []string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	indexNames := strings.Join(indexNameList, ",")
	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexNames + "/_alias")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	alias := make(map[string]interface{})
	for name, obj := range result {
		if aliases, ok := obj.(map[string]interface{})["aliases"]; ok {
			names := make([]string, 0)
			for aliasName := range aliases.(map[string]interface{}) {
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
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetTasks() *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个集群"}
	}
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Get(es.ConnectObj.Host + TasksApi)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultsResp{Err: string(resp.Body())}
	}
	nodes := result["nodes"].(map[string]interface{})

	var data []interface{}
	for _, nodeObj := range nodes {
		nodeTasks, ok := nodeObj.(map[string]interface{})["tasks"].(map[string]interface{})
		if !ok {
			continue
		}
		for taskID, taskInfo := range nodeTasks {
			taskInfoMap := taskInfo.(map[string]interface{})
			data = append(data, map[string]interface{}{
				"task_id":               taskID,
				"node_name":             nodeObj.(map[string]interface{})["name"],
				"node_ip":               nodeObj.(map[string]interface{})["ip"],
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
	var result map[string]interface{}

	resp, err := es.Client.R().SetResult(&result).Post(newUrl)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	return &types.ResultResp{Result: result}
}
