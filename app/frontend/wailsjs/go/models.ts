export namespace types {
	
	export class Connect {
	    ConnectName: string;
	    Host: string;
	    Username: string;
	    Password: string;
	
	    static createFrom(source: any = {}) {
	        return new Connect(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ConnectName = source["ConnectName"];
	        this.Host = source["Host"];
	        this.Username = source["Username"];
	        this.Password = source["Password"];
	    }
	}
	export class Config {
	    width: number;
	    height: number;
	    language: string;
	    theme: string;
	    connects: Connect[];
	
	    static createFrom(source: any = {}) {
	        return new Config(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.width = source["width"];
	        this.height = source["height"];
	        this.language = source["language"];
	        this.theme = source["theme"];
	        this.connects = this.convertValues(source["connects"], Connect);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
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

