
const save_gists = async (visibility, description, expiration, categories, address, files) => {
  const payload = {
    "metadata": {
      "visibility": visibility,
      "description": description,
      "expiration": expiration,
      "categories": categories,
      "user_address": address
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
  if (document.contxt.codemirror.getValue().length === 0) {
    alert('No content provided');
    return;
  }

  const files = [
    {name: 'basic.txt', content: document.contxt.codemirror.getValue() }
  ];

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
