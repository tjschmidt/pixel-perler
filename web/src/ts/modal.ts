/// <reference path="vendor/jquery-3.2.1.min.js"/>

class Modal {
    jq: JQuery;

    constructor(readonly content: string, wrapContent: boolean = true) {
        let html;
        if (wrapContent)
            html = '<div class="fs-modal"><div class="modal-content">' + content + '</div></div>';
        else
            html = content;
        this.jq = $(html);
    }

    show(): void {
        $('body').append(this.jq);
    }

    hide(): void {
        this.jq.remove();
    }
}

class WaitModal extends Modal {
    constructor() {
        let html = '<div class="fs-modal"><div class="spinner"></div></div>';
        super(html, false);
    }
}

class TitledModal extends Modal {
    constructor(title: string, content: string, dismiss: string = null, callback: (evt: JQuery.Event) => void = null) {
        let html = '<h4 class="title">' + title + '</h4>' + '<span class="content">' + content + '</span>';
        if (dismiss != null) {
            html += '<div class="flex center-h"><button class="button rounded">' + dismiss + '</button></div>';
        }
        super(html);
        let self = this;
        this.jq.find('button').click(function (e) {
            if (callback != null)
                callback(e);
            self.hide();
        });
    }
}
