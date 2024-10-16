import {ref, onMounted} from 'vue'
import axios from 'axios'

export const FORMAT = "?format=json&pretty";
export const STATS_API = "_cluster/stats" + FORMAT;
export const HEALTH_API = "_cluster/health";
export const NODES_API = "_cat/nodes?format=json&pretty&h=ip,name,heap.percent,heap.current,heap.max,ram.percent,ram.current,ram.max,node.role,master,cpu,load_5m,disk.used_percent,disk.used,disk.total,fielddataMemory,queryCacheMemory,requestCacheMemory,segmentsMemory,segments.count";
export const ALL_INDEX_API = "_cat/indices?format=json&pretty&bytes=b";
export const CLUSTER_SETTINGS = "_cluster/settings";
export const FORCE_MERGE = "_forcemerge?wait_for_completion=false"; // 异步
export const REFRESH = "_refresh";
export const FLUSH = "_flush";
export const CACHE_CLEAR = "_cache/clear";
export const TASKS_API = "_tasks" + FORMAT;
export const CANCEL_TASKS_API = "_tasks/{task_id}/_cancel";

const esService = {

    // 初始化连接信息
    setConnect(key, host, username, pwd) {
        this.connectName = key;
        this.connectObj = {
            host,
            username,
            pwd
        };
        this.auth = {username, password: pwd};
        console.log('设置当前连接：', this.connectObj.host);
    },

    // 测试连接
    async testClient(host, username, pwd) {
        try {
            console.log('测试连接：', `${host}/${HEALTH_API}`);
            const res = await axios.get(`${host}/${HEALTH_API}`, {
                auth: {username, password: pwd}
            });
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, null];
        } catch (e) {
            return [false, e.message];
        }
    },

    // 获取集群节点信息
    async getNodes() {
        const res = await axios.get(`${this.connectObj.host}${NODES_API}`, {auth: this.auth});
        return res.data;
    },

    // 获取集群健康信息
    async getHealth() {
        const res = await axios.get(`${this.connectObj.host}${HEALTH_API}`, {auth: this.auth});
        return res.data;
    },

    // 获取集群统计信息
    async getStats() {
        const res = await axios.get(`${this.connectObj.host}${STATS_API}`, {auth: this.auth});
        return res.data;
    },

    // 获取索引信息
    async getIndexes(name = null) {
        const url = `${this.connectObj.host}${ALL_INDEX_API}${name ? `&index=${name}` : ''}`;
        try {
            const res = await axios.get(url, {auth: this.auth});
            if (res.status === 404) {
                return [];
            }
            return res.data;
        } catch (error) {
            console.error(error);
            return [];
        }
    },

    // 创建索引
    async createIndex(name, number_of_shards = 1, number_of_replicas = 0) {
        const indexConfig = {
            settings: {
                number_of_shards,
                number_of_replicas
            }
        };
        try {
            const res = await axios.put(`${this.connectObj.host}/${name}`, indexConfig, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, null];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

    // 获取索引信息
    async getIndexInfo(indexName) {
        try {
            const res = await axios.get(`${this.connectObj.host}/${indexName}`, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

    // 删除索引
    async deleteIndex(indexName) {
        try {
            const res = await axios.delete(`${this.connectObj.host}/${indexName}`, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 开启/关闭索引
    async openCloseIndex(indexName, action) {
        try {
            const res = await axios.post(`${this.connectObj.host}/${indexName}/${action}`, {}, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 获取索引mappings
    async getIndexMappings(indexName) {
        try {
            const res = await axios.get(`${this.connectObj.host}/${indexName}`, {auth: this.auth});
            return res.data;
        } catch (error) {
            console.error(error);
            return {};
        }
    },

// 合并段落
    async mergeSegments(indexName) {
        try {
            const res = await axios.post(`${this.connectObj.host}/${indexName}/${FORCE_MERGE}`, {}, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 刷新索引
    async refresh(indexName) {
        try {
            const res = await axios.post(`${this.connectObj.host}/${indexName}/${REFRESH}`, {}, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 刷新索引
    async flush(indexName) {
        try {
            const res = await axios.post(`${this.connectObj.host}/${indexName}/${FLUSH}`, {}, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 清理缓存
    async cacheClear(indexName) {
        try {
            const res = await axios.post(`${this.connectObj.host}/${indexName}/${CACHE_CLEAR}`, {}, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 获取前10条文档
    async getDoc10(indexName) {
        try {
            const res = await axios.post(`${this.connectObj.host}/${indexName}/_search`, {
                query: {
                    query_string: {
                        query: "*"
                    }
                },
                size: 10,
                from: 0,
                sort: []
            }, {auth: this.auth});

            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 自定义搜索
    async search(method, path, body) {
        try {
            const res = await axios.request({
                method,
                url: `${this.connectObj.host}/${path}`,
                data: body,
                auth: this.auth
            });
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 获取集群设置
    async getClusterSettings() {
        try {
            const res = await axios.get(`${this.connectObj.host}/${CLUSTER_SETTINGS}`, {auth: this.auth});
            return res.data;
        } catch (error) {
            console.error(error);
            return {};
        }
    },

// 获取索引设置
    async getIndexSettings(indexName) {
        try {
            const res = await axios.get(`${this.connectObj.host}/${indexName}`, {auth: this.auth});
            return res.data;
        } catch (error) {
            console.error(error);
            return {};
        }
    },

// 获取索引别名
    async getIndexAliases(indexNameList) {
        const indexNames = indexNameList.join(',');
        try {
            const res = await axios.get(`${this.connectObj.host}/${indexNames}/_alias`, {auth: this.auth});
            const data = res.data;
            const aliases = {};
            for (const name in data) {
                const names = Object.keys(data[name].aliases);
                if (names.length > 0) {
                    aliases[name] = names.join(',');
                }
            }
            return aliases;
        } catch (error) {
            console.error(error);
            return {};
        }
    },

// 获取索引段落
    async getIndexSegments(indexName) {
        try {
            const res = await axios.get(`${this.connectObj.host}/${indexName}/_segments`, {auth: this.auth});
            return res.data;
        } catch (error) {
            console.error(error);
            return {};
        }
    },

// 获取任务列表
    async getTasks() {
        try {
            const res = await axios.get(`${this.connectObj.host}/${TASKS_API}`, {auth: this.auth});
            const data = res.data.nodes;
            const tasks = [];
            for (const nodeID in data) {
                const node = data[nodeID];
                for (const taskID in node.tasks) {
                    const task = node.tasks[taskID];
                    tasks.push({
                        task_id: taskID,
                        node_name: node.name,
                        node_ip: node.ip,
                        type: task.type,
                        action: task.action,
                        start_time_in_millis: task.start_time_in_millis,
                        running_time_in_nanos: task.running_time_in_nanos,
                        cancellable: task.cancellable,
                        parent_task_id: task.parent_task_id || ""
                    });
                }
            }
            return [true, tasks];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

// 取消任务
    async cancelTasks(taskId) {
        try {
            const res = await axios.post(`${this.connectObj.host}/${CANCEL_TASKS_API.replace('{task_id}', taskId)}`, {}, {auth: this.auth});
            if (res.status !== 200) {
                return [false, res.statusText];
            }
            return [true, res.data];
        } catch (e) {
            console.error(e);
            return [false, e.message];
        }
    },

};


export default esService;