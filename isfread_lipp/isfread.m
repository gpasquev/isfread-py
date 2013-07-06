function [t,v,head] = isfread(filename)

% This function loads the binary data from a Tektronix ".ISF"
% file.  The ISF file format is used by newer Tektronix
% TDS-series oscilloscopes.
% 
% Syntax:
%   [t,v] = isfread(filename);
%   [t,v,head] = isfread(filename);
%
% Input:
%   filename - name of Tektronix ISF file
%
% Outputs:
%   t - time data vector
%   v - voltage data vector.  If format is 'ENV' (envelope), two columns
%       are returned: [vmax vmin]
%   head - (optional) header record of file

if ~exist(filename,'file')
    error(sprintf('%s not found.',filename));
end;

FID = fopen(filename,'r');

hdata = fread(FID,511,'char')';			% read first 511 bytes
hdata = min(hdata,126);					% eliminate non-ascii
hdata = max(hdata,9);					% characters from header data
hdata = char(hdata);					% convert to character string

bytenum = getnum(hdata,'BYT_NR');
bitnum = getnum(hdata,'BIT_NR');
encoding = getstr(hdata,'ENCDG');
binformat = getstr(hdata,'BN_FMT');
byteorder = getstr(hdata,'BYT_OR');
wfid = getquotedstr(hdata,'WFID');
pointformat = getstr(hdata,'PT_FMT');
xunit = getquotedstr(hdata,'XUNIT');
yunit = getquotedstr(hdata,'YUNIT');
xzero = getnum(hdata,'XZERO');
xincr = getnum(hdata,'XINCR');
ptoff = getnum(hdata,'PT_OFF');
ymult = getnum(hdata,'YMULT');
yzero = getnum(hdata,'YZERO');
yoff = getnum(hdata,'YOFF');
npts = getnum(hdata,'NR_PT');

% New format (e.g. Tek DPO3000 series, 2009) changed several formats...
if isempty(npts)
    bytenum = getnum(hdata,'BYT_N');
    bitnum = getnum(hdata,'BIT_N');
    encoding = getstr(hdata,'ENC');
    binformat = getstr(hdata,'BN_F');
    byteorder = getstr(hdata,'BYT_O');
    wfid = getquotedstr(hdata,'WFI');
    pointformat = getstr(hdata,'PT_F');
    xunit = getquotedstr(hdata,'XUN');
    yunit = getquotedstr(hdata,'YUN');
    xzero = getnum(hdata,'XZE');
    xincr = getnum(hdata,'XIN');
    ptoff = getnum(hdata,'PT_O');
    ymult = getnum(hdata,'YMU');
    yzero = getnum(hdata,'YZE');
    yoff = getnum(hdata,'YOF');
    npts = getnum(hdata,'NR_P');
end;

if ((bytenum ~= 2) | ...
	(bitnum ~= 16) | ...
	not(strcmp(encoding,'BIN')) | ...
	not(strcmp(binformat,'RI')))
  fclose(FID);
  error('Unable to process IFS file.');
end

% This fails if PT_FMT == 'ENV', which is not nice
% if ((bytenum ~= 2) | ...
% 	(bitnum ~= 16) | ...
% 	not(strcmp(encoding,'BIN')) | ...
% 	not(strcmp(binformat,'RI')) | ...
% 	not(strcmp(pointformat,'Y')))
%   fclose(FID);
%   error('Unable to process IFS file.');
% end

switch byteorder
  case 'MSB'
    machineformat = 'b';
  case 'LSB'
    machineformat = 'l';
  otherwise,
    error('Unrecognized byte order.');
end

ii = strfind(hdata,'#');

% Fix for reading files from older scopes
%fseek(FID,ii,'bof');					% advance to start of data
fseek(FID,ii(1),'bof');					% advance to start of data
skip = str2num(char(fread(FID,1,'char')));
fread(FID,skip);
data = fread(FID, npts, 'int16', machineformat);

% If ENV format (envelope), separate into max and min
if pointformat == 'ENV'
    disp('Envelope format: voltage output = [vmax vmin]');
    npts = round(npts/2);
    vmin = yzero + ymult*(data(1:2:end) - yoff);
    vmax = yzero + ymult*(data(2:2:end) - yoff);
    t = xzero + xincr*(0:npts-1)'*2;  % 2 data points per increment
    t = t - min(t);
    v = [vmax vmin];
else
    v = yzero + ymult*(data - yoff);
    t = xzero + xincr*(0:npts-1)';
    t = t - min(t);
end;

fclose(FID);

if (nargout > 2)
  head.bytenum = bytenum;
  head.bitnum = bitnum;
  head.encoding = encoding;
  head.binformat = binformat;
  head.byteorder = byteorder;
  head.wfid = wfid;
  head.pointformat = pointformat;
  head.xunit = xunit;
  head.yunit = yunit;
  head.xzero = xzero;
  head.xincr = xincr;
  head.ptoff = ptoff;
  head.ymult = ymult;
  head.yzero = yzero;
  head.yoff = yoff;
  head.npts = npts;
end


function z = getnum(str,pattern)
ii = strfind(str,pattern) + length(pattern);
tmp = strtok(str(ii:length(str)),';');
z = str2num(tmp);


function z = getstr(str,pattern)
ii = strfind(str,pattern) + length(pattern) + 1;
z = strtok(str(ii:length(str)),';');


function z = getquotedstr(str,pattern)
ii = strfind(str,pattern) + length(pattern) + 1;
z = strtok(str(ii:length(str)),'"');
z = strtok(str(ii:length(str)),'"');

