function getSheetUrl() {
  var SS = SpreadsheetApp.getActiveSpreadsheet();
  var ss = SS.getActiveSheet();
  var url = '';
  url += SS.getUrl().replace('/edit', '');
  //url += '#gid=';
  //url += ss.getSheetId();
  return url;
}
