package service

import (
	"app/backend/types"
	"encoding/json"
	"fmt"
	"net/url"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
)

const (
	FORMAT          = "?format=json&pretty"
	StatsApi        = "_cluster/stats" + FORMAT
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
		Client: client,
	}
}

func (es *ESService) SetConnect(key, host, username, pwd string) {
	es.ConnectObj = &types.Connect{
		ConnectName: key,
		Host:        host,
		Username:    username,
		Password:    pwd,
	}
	es.Client.SetBasicAuth(username, pwd)
	fmt.Println("设置当前连接：", es.ConnectObj.Host)
}

func (es *ESService) TestClient(host, username, pwd string) string {
	client := resty.New().SetBasicAuth(username, pwd)
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

func (es *ESService) CreateIndex(name string, numberOfShards, numberOfReplicas int) (bool, string) {
	indexConfig := map[string]interface{}{
		"settings": map[string]interface{}{
			"number_of_shards":   numberOfShards,
			"number_of_replicas": numberOfReplicas,
		},
	}
	resp, err := es.Client.R().
		SetBody(indexConfig).
		Put(es.ConnectObj.Host + name)
	if err != nil {
		return false, err.Error()
	}
	if resp.StatusCode() != 200 {
		return false, string(resp.Body())
	}
	return true, ""
}

func (es *ESService) GetIndexInfo(indexName string) (bool, map[string]interface{}) {
	resp, err := es.Client.R().Get(es.ConnectObj.Host + indexName)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) DeleteIndex(indexName string) (bool, map[string]interface{}) {
	resp, err := es.Client.R().Delete(es.ConnectObj.Host + indexName)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) OpenCloseIndex(indexName, now string) (bool, map[string]interface{}) {
	action := map[string]string{
		"open":  "_close",
		"close": "_open",
	}[now]
	resp, err := es.Client.R().Post(es.ConnectObj.Host + indexName + "/" + action)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) GetIndexMappings(indexName string) (map[string]interface{}, error) {
	resp, err := es.Client.R().Get(es.ConnectObj.Host + indexName)
	if err != nil {
		return nil, err
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return result, err
}

func (es *ESService) MergeSegments(indexName string) (bool, map[string]interface{}) {
	resp, err := es.Client.R().Post(es.ConnectObj.Host + indexName + "/" + ForceMerge)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) Refresh(indexName string) (bool, map[string]interface{}) {
	resp, err := es.Client.R().Post(es.ConnectObj.Host + indexName + "/" + REFRESH)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) Flush(indexName string) (bool, map[string]interface{}) {
	resp, err := es.Client.R().Post(es.ConnectObj.Host + indexName + "/" + FLUSH)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) CacheClear(indexName string) (bool, map[string]interface{}) {
	resp, err := es.Client.R().Post(es.ConnectObj.Host + indexName + "/" + CacheClear)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) GetDoc10(indexName string) (bool, map[string]interface{}) {
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
		Post(es.ConnectObj.Host + indexName + "/_search")
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) Search(method, path string, body interface{}) (bool, map[string]interface{}) {
	resp, err := es.Client.R().
		SetBody(body).
		Execute(method, es.ConnectObj.Host+path)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}

func (es *ESService) GetClusterSettings() (map[string]interface{}, error) {
	resp, err := es.Client.R().Get(es.ConnectObj.Host + ClusterSettings)
	if err != nil {
		return nil, err
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return result, err
}

func (es *ESService) GetIndexSettings(indexName string) (map[string]interface{}, error) {
	resp, err := es.Client.R().Get(es.ConnectObj.Host + indexName)
	if err != nil {
		return nil, err
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return result, err
}

func (es *ESService) GetIndexAliases(indexNameList []string) map[string]string {
	indexNames := strings.Join(indexNameList, ",")
	resp, err := es.Client.R().Get(es.ConnectObj.Host + indexNames + "/_alias")
	if err != nil {
		return map[string]string{}
	}
	var data map[string]interface{}
	err = json.Unmarshal(resp.Body(), &data)
	if err != nil {
		return map[string]string{}
	}
	alias := make(map[string]string)
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
	return alias
}

func (es *ESService) GetIndexSegments(indexName string) (map[string]interface{}, error) {
	resp, err := es.Client.R().Get(es.ConnectObj.Host + indexName)
	if err != nil {
		return nil, err
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	return result, err
}

func (es *ESService) GetTasks() (bool, []map[string]interface{}) {
	resp, err := es.Client.R().Get(es.ConnectObj.Host + TasksApi)
	if err != nil {
		return false, nil
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, nil
	}
	nodes, ok := result["nodes"].(map[string]interface{})
	if !ok {
		return false, nil
	}
	data := make([]map[string]interface{}, 0)
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
	return true, data
}

func (es *ESService) CancelTasks(taskID string) (bool, map[string]interface{}) {
	newUrl := fmt.Sprintf(es.ConnectObj.Host+CancelTasksApi, url.PathEscape(taskID))
	resp, err := es.Client.R().Post(newUrl)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	if resp.StatusCode() != 200 {
		return false, map[string]interface{}{"error": string(resp.Body())}
	}
	var result map[string]interface{}
	err = json.Unmarshal(resp.Body(), &result)
	if err != nil {
		return false, map[string]interface{}{"error": err.Error()}
	}
	return true, result
}
