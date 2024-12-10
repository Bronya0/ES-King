package types

type Tag struct {
	TagName string `json:"tag_name"`
	Body    string `json:"body"`
}
type Config struct {
	Width    int       `json:"width"`
	Height   int       `json:"height"`
	Language string    `json:"language"`
	Theme    string    `json:"theme"`
	Connects []Connect `json:"connects"`
}
type History struct {
	Time   int    `json:"timestamp"`
	Method string `json:"method"`
	Path   string `json:"path"`
	DSL    string `json:"dsl"`
}
type ResultsResp struct {
	Results []any  `json:"results"`
	Err     string `json:"err"`
}
type ResultResp struct {
	Result map[string]any `json:"result"`
	Err    string         `json:"err"`
}
type Connect struct {
	Id            int    `json:"id"`
	Name          string `json:"name"`
	Host          string `json:"host"`
	Username      string `json:"username"`
	Password      string `json:"password"`
	UseSSL        bool   `json:"useSSL"`
	SkipSSLVerify bool   `json:"skipSSLVerify"`
	CACert        string `json:"caCert"`
}
type H map[string]any
