export namespace types {
	
	export class Config {
	    width: number;
	    height: number;
	    language: string;
	    theme: string;
	
	    static createFrom(source: any = {}) {
	        return new Config(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.width = source["width"];
	        this.height = source["height"];
	        this.language = source["language"];
	        this.theme = source["theme"];
	    }
	}
	export class ResultResp {
	    result: {[key: string]: any};
	    err: string;
	
	    static createFrom(source: any = {}) {
	        return new ResultResp(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.result = source["result"];
	        this.err = source["err"];
	    }
	}
	export class ResultsResp {
	    results: any[];
	    err: string;
	
	    static createFrom(source: any = {}) {
	        return new ResultsResp(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.results = source["results"];
	        this.err = source["err"];
	    }
	}
	export class Tag {
	    tag_name: string;
	    body: string;
	
	    static createFrom(source: any = {}) {
	        return new Tag(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.tag_name = source["tag_name"];
	        this.body = source["body"];
	    }
	}

}

