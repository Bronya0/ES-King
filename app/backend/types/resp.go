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
