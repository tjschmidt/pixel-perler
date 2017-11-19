/// <reference path="feature.ts"/>
/// <reference path="modal.ts"/>
/// <reference path="vendor/jquery-3.2.1.min.js"/>

function fileUpload(form: HTMLFormElement, fileInput: JQuery, callback: (json) => void, maxSize: number = Math.pow(2, 30)): void {
    let droppedFile = null;

    if (!(form.get(0) instanceof HTMLFormElement)) {
        console.log('Invalid form element');
        return;
    }

    let fileTooLargeModal = new TitledModal('Upload Error', 'Your image exceeds the maximum upload size. ' +
        'Reduce the size of your image and try again.', 'OK');

    if (canDragAndDrop()) {
        form.addClass('advanced');

        form.on('drag dragstart dragend dragover dragenter dragleave drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
        })
            .on('dragover dragenter', function () {
                form.addClass('dragover');
            })
            .on('dragleave dragend drop', function () {
                form.removeClass('dragover');
            })
            .on('drop', function (e: JQuery.Event) {
                droppedFile = e.originalEvent.dataTransfer.files[0];
                if (droppedFile.size > maxSize) {
                    fileTooLargeModal.show();
                } else {
                    form.trigger('submit');
                }
            });


    }

    fileInput.on('change', function () {
        form.trigger('submit');
    });

    form.on('submit', function (e: JQuery.Event) {
        if (form.hasClass('uploading'))
            return false;

        form.addClass('uploading');

        if (canDragAndDrop()) {
            e.preventDefault();

            let ajaxData = new FormData(form.get(0));

            if (droppedFile !== null) {
                ajaxData.append(fileInput.attr('name'), droppedFile);
            } else {
                let files = fileInput[0].files;
                if (files.length > 0 && files[0].size > maxSize) {
                    fileTooLargeModal.show();
                    return;
                }
            }

            $.ajax({
                url: form.attr('action'),
                type: form.attr('method'),
                data: ajaxData,
                dataType: 'json',
                cache: false,
                contentType: false,
                processData: false,
                complete: function () {
                    form.removeClass('uploading');
                },
                success: function (data) {
                    callback(data);
                },
                error: function () {
                    console.log('Error occurred');
                }
            });

        } else {

            let files = fileInput[0].files;
            if (files.length > 0 && files[0].size > maxSize) {
                fileTooLargeModal.show();
                return;
            }

            let iframeName = 'uploadiframe' + new Date().getTime();
            let iframe = $('<iframe name="' + iframeName + '" style="display: none;"></iframe>');
            $('body').append(iframe);
            form.attr('target', iframeName);

            iframe.one('load', function () {
                let data = JSON.parse(iframe.contents().find('body').text());
                form
                    .removeClass('uploading')
                    .addClass(data.success === true ? 'success' : 'error')
                    .removeAttr('target');
                iframe.remove();
            });
        }
    });
}
