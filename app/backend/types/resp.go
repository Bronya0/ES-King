package types

type Tag struct {
	TagName string `json:"tag_name"`
	Body    string `json:"body"`
}
type Config struct {
	Width    int    `json:"width"`
	Height   int    `json:"height"`
	Language string `json:"language"`
	Theme    string `json:"theme"`
}
type ResultsResp struct {
	Results []interface{} `json:"results"`
	Err     string        `json:"err"`
}
type ResultResp struct {
	Result map[string]interface{} `json:"result"`
	Err    string                 `json:"err"`
}
