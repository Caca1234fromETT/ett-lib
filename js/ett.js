ett = {
    get: async function(page) {
        return await fetch("https://tikolu.net/edit/.text/" + page).then(response => response.text());
    },
    post: async function(page, content) {
        await fetch("https://tikolu.net/edit/" + page, {
        method: "POST",
        body: JSON.stringify({content: content, timestamp: 0, ignoreconflict: true})
        });
    }
}

class Virtual {
    constructor(speed) {
        this.pages = [];
        this.speed = speed; // mbit/s
    }
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    async get(page) {
        if (!this.pages[page]) {
            var content = ett.get(page);
            this.pages[page] = content;
	        
            await this.sleep(content.length / this.speed);
	        
            return content;
        }
        var content = this.pages[page];
	    
        await this.sleep(content.length / this.speed);
	    
        return content;
    }
    async post(page, content) {
        await this.sleep(content.length / this.speed);
        this.pages[page] = content;
    }
}
