import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  token: string | null;
  tenant_id: string | null;
  role: string | null;
  isAuthenticated: boolean;
}

const getInitialState = (): AuthState => {
  let token = null;
  let tenant_id = null;
  let role = null;
  
  if (typeof window !== 'undefined') {
    token = localStorage.getItem('aiekp_token');
    tenant_id = localStorage.getItem('aiekp_tenant_id');
    role = localStorage.getItem('aiekp_role');
  }

  return {
    token,
    tenant_id,
    role,
    isAuthenticated: !!token,
  };
};

export const authSlice = createSlice({
  name: 'auth',
  initialState: getInitialState(),
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ token: string; tenant_id: string; role: string }>
    ) => {
      state.token = action.payload.token;
      state.tenant_id = action.payload.tenant_id;
      state.role = action.payload.role;
      state.isAuthenticated = true;

      if (typeof window !== 'undefined') {
        localStorage.setItem('aiekp_token', action.payload.token);
        localStorage.setItem('aiekp_tenant_id', action.payload.tenant_id);
        localStorage.setItem('aiekp_role', action.payload.role);
      }
    },
    logout: (state) => {
      state.token = null;
      state.tenant_id = null;
      state.role = null;
      state.isAuthenticated = false;

      if (typeof window !== 'undefined') {
        localStorage.removeItem('aiekp_token');
        localStorage.removeItem('aiekp_tenant_id');
        localStorage.removeItem('aiekp_role');
      }
    },
  },
});

export const { setCredentials, logout } = authSlice.actions;

export default authSlice.reducer;
