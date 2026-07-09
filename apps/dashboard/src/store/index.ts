import { configureStore } from '@reduxjs/toolkit'
import { aiekpApi } from './api/aiekpApi'
import graphReducer from './graphSlice'
import authReducer from './authSlice'

export const store = configureStore({
  reducer: {
    [aiekpApi.reducerPath]: aiekpApi.reducer,
    graph: graphReducer,
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(aiekpApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
