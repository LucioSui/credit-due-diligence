import React, { useState, useCallback } from 'react';
import { Autocomplete, TextField, CircularProgress, Box } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

interface CompanySearchProps {
  onSelect: (name: string) => void;
  value?: string;
}

interface CompanyOption {
  id: string;
  label: string;
  credit_code?: string;
}

const CompanySearch: React.FC<CompanySearchProps> = ({ onSelect, value: externalValue }) => {
  const [inputValue, setInputValue] = useState(externalValue ?? '');
  const [options, setOptions] = useState<CompanyOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [_open, setOpen] = useState(false);

  const handleSearch = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setOptions([]);
      return;
    }
    setLoading(true);
    try {
      // TODO: replace with actual API call to search companies
      // For now, use mock data
      await new Promise((resolve) => setTimeout(resolve, 300));
      const mockResults: CompanyOption[] = [
        { id: '1', label: `${query}科技有限公司`, credit_code: '91110108MA0XXXXX' },
        { id: '2', label: `${query}集团有限公司`, credit_code: '91110108MA0YYYYY' },
        { id: '3', label: `${query}商贸有限公司`, credit_code: '91110108MA0ZZZZZ' },
      ];
      setOptions(mockResults);
    } catch {
      setOptions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (_event: React.SyntheticEvent, value: CompanyOption | null) => {
    if (value) {
      setInputValue(value.label);
      onSelect(value.label);
      setOpen(false);
    }
  };

  const handleInputChange = (_event: React.SyntheticEvent, newValue: string) => {
    setInputValue(newValue);
    handleSearch(newValue);
  };

  const handleOpenChange = (_event: React.SyntheticEvent) => {
    setOpen(true);
    if (inputValue.length >= 2) {
      handleSearch(inputValue);
    }
  };

  return (
    <Autocomplete
      options={options}
      value={options.find((opt) => opt.label === inputValue) ?? null}
      getOptionLabel={(option) =>
        typeof option === 'string' ? option : option.label
      }
      onChange={handleChange}
      onInputChange={handleInputChange}
      onOpen={handleOpenChange}
      onClose={() => {}}
      loading={loading}
      isOptionEqualToValue={(option, value) => option.id === value.id}
      renderInput={(params) => (
        <TextField
          {...params}
          label="搜索企业名称"
          placeholder="输入企业名称或信用代码"
          size="small"
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <>
                <SearchIcon sx={{ mr: 1, color: 'action.active', fontSize: 20 }} />
                {params.InputProps.startAdornment}
              </>
            ),
            endAdornment: (
              <>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
      renderOption={(props, option) => (
        <Box component="li" {...props}>
          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: 500 }}>{option.label}</span>
            {option.credit_code && (
              <span style={{ fontSize: '0.75rem', color: '#999' }}>{option.credit_code}</span>
            )}
          </Box>
        </Box>
      )}
    />
  );
};

export default CompanySearch;
