import {request} from './client';import type {Dataset,Revision,CorrectionInput,CorrectionResult} from '../types/domain';
export const list=()=>request<Dataset[]>('/datasets');
export const create=(data:unknown)=>request<Dataset>('/datasets',data);
export const revisions=(id:string)=>request<Revision[]>('/datasets/'+id+'/revisions');
export const correct=(id:string,data:CorrectionInput)=>request<CorrectionResult>('/datasets/'+id+'/revisions',data);
