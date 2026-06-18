export const downloadBase64File = (base64String, filename, mimeType) => {
  // Decode the base64 string
  const byteCharacters = atob(base64String.split(',')[1] || base64String); // Handle potential data URL prefix
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);

  // Create a Blob from the byte array
  const blob = new Blob([byteArray], { type: mimeType });

  // Create a URL for the Blob and initiate download
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url); // Clean up the object URL
};