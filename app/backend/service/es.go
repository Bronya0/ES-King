package service

import (
	"app/backend/types"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"fmt"
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
	return &ESService{
		Client:     client,
		ConnectObj: &types.Connect{},
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
	// Configure SSL
	if UseSSL {
		es.Client.SetScheme("https")
		if SkipSSLVerify {
			es.Client.SetTLSClientConfig(&tls.Config{InsecureSkipVerify: true})
		}
		if CACert != "" {
			caCertPool := x509.NewCertPool()
			caCertPool.AppendCertsFromPEM([]byte(CACert))
			es.Client.SetRootCertificate(CACert)
		}
	} else {
		es.Client.SetScheme("http")
	}
	fmt.Println("设置当前连接：", es.ConnectObj.Host)
}

func (es *ESService) TestClient(host, username, password, CACert string, UseSSL, SkipSSLVerify bool) string {
	client := resty.New()
	if username != "" && password != "" {
		client.SetBasicAuth(username, password)
	}
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
		return &types.ResultsResp{Err: "请先选择一个连接"}
	}
	resp, err := es.Client.R().Get(es.ConnectObj.Host + NodesApi)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	var result []interface{}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}
	return &types.ResultsResp{Results: result}
}

func (es *ESService) GetHealth() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}
	resp, err := es.Client.R().Get(es.ConnectObj.Host + HealthApi)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	var result map[string]interface{}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetStats() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}
	resp, err := es.Client.R().Get(es.ConnectObj.Host + StatsApi)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	var result map[string]interface{}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexes(name string) *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个连接"}
	}
	newUrl := es.ConnectObj.Host + AllIndexApi
	if name != "" {
		newUrl += "&index=" + name
	}
	resp, err := es.Client.R().Get(newUrl)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}
	}

	var result []interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return &types.ResultsResp{Results: result}

}

func (es *ESService) CreateIndex(name string, numberOfShards, numberOfReplicas int) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	indexConfig := map[string]interface{}{
		"settings": map[string]interface{}{
			"number_of_shards":   numberOfShards,
			"number_of_replicas": numberOfReplicas,
		},
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
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) DeleteIndex(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Delete(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) OpenCloseIndex(indexName, now string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	action := map[string]string{
		"open":  "_close",
		"close": "_open",
	}[now]
	resp, err := es.Client.R().Post(es.ConnectObj.Host + "/" + indexName + "/" + action)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) GetIndexMappings(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return &types.ResultResp{Result: result}

}

func (es *ESService) MergeSegments(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Post(es.ConnectObj.Host + "/" + indexName + ForceMerge)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}
	}
	return &types.ResultResp{Result: result}

}

func (es *ESService) Refresh(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Post(es.ConnectObj.Host + "/" + indexName + REFRESH)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) Flush(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Post(es.ConnectObj.Host + "/" + indexName + FLUSH)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) CacheClear(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Post(es.ConnectObj.Host + "/" + indexName + CacheClear)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetDoc10(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
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
	resp, err := es.Client.R().
		SetBody(body).
		Post(es.ConnectObj.Host + "/" + indexName + "/_search")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) Search(method, path string, body interface{}) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().
		SetBody(body).
		Execute(method, es.ConnectObj.Host+path)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}

	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetClusterSettings() *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Get(es.ConnectObj.Host + ClusterSettings)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexSettings(indexName string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetIndexAliases(indexNameList []string) *types.ResultResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	indexNames := strings.Join(indexNameList, ",")
	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/" + indexNames + "/_alias")
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	var data map[string]interface{}
	err = json.Unmarshal(resp.Body(), &data)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	alias := make(map[string]interface{})
	for name, obj := range data {
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
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Get(es.ConnectObj.Host + "/" + indexName)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return &types.ResultResp{Result: result}
}

func (es *ESService) GetTasks() *types.ResultsResp {
	if es.ConnectObj.Host == "" {
		return &types.ResultsResp{Err: "请先选择一个连接"}
	}

	resp, err := es.Client.R().Get(es.ConnectObj.Host + TasksApi)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}

	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultsResp{Err: err.Error()}

	}
	nodes, _ := result["nodes"].(map[string]interface{})

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
		return &types.ResultResp{Err: "请先选择一个连接"}
	}

	newUrl := fmt.Sprintf(es.ConnectObj.Host+CancelTasksApi, url.PathEscape(taskID))
	resp, err := es.Client.R().Post(newUrl)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	if resp.StatusCode() != 200 {
		return &types.ResultResp{Err: string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return &types.ResultResp{Err: err.Error()}

	}
	return &types.ResultResp{Result: result}
}
