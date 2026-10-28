import { FONT } from '../theme.js';
import fs from 'node:fs';
export const P = { blue:'014F9C', navy:'17406D', ink:'1C2632', gray:'697A89', light:'ECF5FC', line:'CBD8E4', red:'B3262D', rose:'FCF1F0', teal:'176C7B', amber:'A67218', cream:'FBF5E9', white:'FFFFFF' };
type Slide = any;
export function txt(s:Slide,t:string,x:number,y:number,w:number,h:number,size=18,color=P.ink,options:any={}) {
  s.addText(t,{x,y,w,h,fontFace:FONT.body,fontSize:size,color,margin:0,valign:'mid',breakLine:false,
    paraSpaceAfterPt:0,lineSpacingMultiple:1.12,...options});
}
export function line(s:Slide,x1:number,y1:number,x2:number,y2:number,color=P.line,width=1,dash=false,arrow=false) {
  s.addShape('line',{x:Math.min(x1,x2),y:Math.min(y1,y2),w:Math.abs(x2-x1),h:Math.abs(y2-y1),
    flipH:x2<x1,flipV:y2<y1,line:{color,width,dashType:dash?'dash':'solid',...(arrow?{endArrowType:'triangle'}:{})}});
}
export function path(s:Slide,points:number[][],color=P.blue,dash=false,width=1.4) {
  for(let i=0;i<points.length-1;i++) line(s,...points[i] as [number,number],...points[i+1] as [number,number],color,width,dash,i===points.length-2);
}
export function rect(s:Slide,x:number,y:number,w:number,h:number,fill=P.white,stroke=P.line,dash=false) {
  s.addShape('rect',{x,y,w,h,fill:{color:fill},line:{color:stroke,width:1.1,dashType:dash?'dash':'solid'}});
}
export function node(s:Slide,t:string,x:number,y:number,w:number,h=.72,color=P.blue,sub='',fill=P.white,size=18) {
  rect(s,x,y,w,h,fill,color);
  if(sub){txt(s,t,x+.12,y+.1,w-.24,.34,size,color,{bold:true,align:'center'});txt(s,sub,x+.12,y+.47,w-.24,h-.55,14,P.ink,{align:'center'});}
  else txt(s,t,x+.12,y+.06,w-.24,h-.12,size,color,{bold:true,align:'center'});
}
export function head(s:Slide,t:string,x:number,y:number,w:number,size=20,color=P.blue) {txt(s,t,x,y,w,.38,size,color,{bold:true});}
export function note(s:Slide,t:string,x:number,y:number,w:number,size=15,color=P.gray,h=.5) {txt(s,t,x,y,w,h,size,color,{valign:'top'});}
export function boundary(s:Slide,label:string,x:number,y:number,w:number,h:number,color=P.gray) {
  rect(s,x,y,w,h,P.white,color,true);txt(s,label,x+.15,y+.08,w-.3,.3,14,color,{bold:true});
}
export function image(s:Slide,pptx:any,p:string,x:number,y:number,w:number,h:number) {
  const png=fs.readFileSync(p),iw=png.readUInt32BE(16),ih=png.readUInt32BE(20);
  const scale=Math.min(w/iw,h/ih),fw=iw*scale,fh=ih*scale;
  s.addImage({path:p,x:x+(w-fw)/2,y:y+(h-fh)/2,w:fw,h:fh});
}
export function table(s:Slide,rows:string[][],x:number,y:number,colW:number[],heights:number[],size=14) {
  const data=rows.map((row,r)=>row.map((text,c)=>({text,options:{
    fill:r===0?P.blue:(r%2===0?'F3F7FA':P.white),color:r===0?P.white:c===0?P.blue:P.ink,
    bold:r===0||c===0,breakLine:false,margin:[.08,.09,.08,.09],fontFace:FONT.body,
  }})));
  s.addTable(data,{x,y,w:colW.reduce((a,b)=>a+b,0),colW,rowH:heights,fontSize:size,fontFace:FONT.body,
    border:{type:'solid',color:P.line,pt:.7},margin:[.08,.09,.08,.09],valign:'middle',
    autoPage:false,paraSpaceAfterPt:0,verbose:false});
}
