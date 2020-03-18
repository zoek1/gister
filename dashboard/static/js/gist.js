
const save_gists = async (visibility, description, expiration, categories, address, files) => {
  const payload = {
    "metadata": {
      "visibility": visibility,
      "description": description,
      "expiration": expiration,
      "categories": categories,
      "address": address
    },
    "files": files
  };

  console.log(payload);
  const response = fetch('/api/v1/gists/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  return (await response).json();
};

const on_submit = async (e) => {
  e.preventDefault();

  const description = $('#description').val();
  const visibility = $(e.target).data('visibility');
  const expiration = $('#expiration').val();
  const categories = [$('#syntax').val()];
  console.log($(e.target))

  const list_files = $(`.file`);
  const files = [];

  for(let i=0; i < list_files.length; i++) {
    const filename = $(list_files[i]).find('#filename');
    const code = $(list_files[i]).find('#editor');
    const syntax = $(list_files[i]).find('#syntax').val()
    if (filename.val().length === 0) {
      filename.addClass('is-invalid')
      alert(`Input field 'Filename' is required`);
      return;
    }

    if (code.val().length === 0) {
      alert(`No content provided in file  ${filename.val()}`);
      return;
    }

    files.push({name: filename.val(), content: code.val(), syntax:  syntax})
  }

  const address = document.contxt.address || '';

  try {
    const resp = await save_gists(visibility, description, expiration, categories, address, files);

    window.location = resp.url
  } catch (e) {
    console.log(e)
    alert('Oh Gosh, something goes wrong! Contact to the dev team')
  }
};


const load_skynet_content = async (url) => {
  const response = await fetch(url)
  return response.text()
};

const get_gists = async (uuid) => {
  const response = await fetch(`/api/v1/gists/${uuid}`);
  const gists = await response.json();

  const pupulated = Promise.all(gists.files.map(async (file) => {
    file[content] = await load_skynet_content(file.skynet_url.replace('sia://', 'https://siasky.net/'));
    return file;
  }))

  return populated;
};

const add_file = (e) => {
  e.preventDefault();
  const id =Math.round((new Date()).getTime() / 1000)
  const template = new_template(id);
  $('.files').append(template);
  $(`#${id} .selectpicker`).selectpicker();
};