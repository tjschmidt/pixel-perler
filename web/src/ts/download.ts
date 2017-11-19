/// <reference path="vendor/jquery-3.2.1.min.js"/>
/// <reference path="modal.ts"/>

function triggerDownload(url: string): void {
    let iframe = $('<iframe style="display: none;" src="' + url + '"></iframe>');
    $('body').append(iframe);
}
