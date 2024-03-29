-- Base
select nr_atendimento,
       ds_tipo_atendimento,
       dt_nascimento,
       nm_social,
       nm_pessoa_fisica,
       dt_entrada,
       dt_alta,
       ds_motivo_alta,
       ds_email,
       nr_ddi_telefone,
       nr_ddd_telefone,
       nr_telefone,
       nr_ramal,
       nr_ddi_fone_adic,
       nr_ddd_fone_adic,
       ds_fone_adic,
       nr_ddi_celular,
       nr_ddd_celular,
       nr_telefone_celular,
       nr_ddi_celular_principal,
       nr_ddd_celular_principal,
       nr_telefone_celular_principal,
       ds_mala_direta,
       ds_classif_setor,
       dt_agenda_consulta,
       ds_status_agenda_consulta,
       ds_tipo_agenda_consulta,
       dt_agenda_exame,
       ds_status_agenda_exame,
       ds_procedimento
  from (select base.nr_atendimento,
               base.ds_tipo_atendimento,
       base.dt_nascimento,
       base.cd_pessoa_fisica cd_pessoa_fisica_base,
       base.nm_social,
       base.nm_pessoa_fisica,
       base.dt_entrada,
       base.dt_alta,
       base.ds_motivo_alta,
       base.ds_email,
       base.nr_ddi_telefone,
       base.nr_ddd_telefone,
       base.nr_telefone,
       base.nr_ramal,
       base.nr_ddi_fone_adic,
       base.nr_ddd_fone_adic,
       base.ds_fone_adic,
       base.nr_ddi_celular,
       base.nr_ddd_celular,
       base.nr_telefone_celular,
       base.nr_ddi_celular_principal,
       base.nr_ddd_celular_principal,
       base.nr_telefone_celular_principal,	   
       base.ds_mala_direta,
       (select vd.ds_valor_dominio
          from tasy.valor_dominio vd
         where vd.cd_dominio = 1
           and vd.vl_dominio = sa.cd_classif_setor) ds_classif_setor,
       min(con.dt_agenda_consulta) over(partition by base.cd_pessoa_fisica, base.nr_atendimento) min_dt_agenda_consulta,
       con.*,
       min(exa.dt_agenda_exame) over(partition by base.cd_pessoa_fisica, base.nr_atendimento) min_dt_agenda_exame,
       exa.*
  from (select ap.nr_atendimento,
               pf.dt_nascimento,
               pf.cd_pessoa_fisica,
               pf.nm_pessoa_fisica,
               pf.nm_social,
               ap.ie_tipo_atendimento,
               substr(tasy.obter_valor_dominio(12, ap.ie_tipo_atendimento),
                      1,
                      254) ds_tipo_atendimento,
               sci.ds_carater_internacao,
               ap.dt_entrada,
               ap.dt_alta,
               ap.cd_motivo_alta,
               tasy.obter_motivo_alta_atend(ap.nr_atendimento) AS ds_motivo_alta,
               (select vd.ds_valor_dominio
                  from tasy.valor_dominio vd
                 where vd.vl_dominio = cpf.ie_tipo_complemento
                   and vd.cd_dominio = 8) tipo_contato,
               cpf.nm_contato,
               cpf.ds_email,
               cpf.nr_ddi_telefone,
               cpf.nr_ddd_telefone,
               cpf.nr_telefone,
               cpf.nr_ramal,
               cpf.nr_ddi_fone_adic,
               cpf.nr_ddd_fone_adic,
               cpf.ds_fone_adic,
               cpf.nr_ddi_celular,
               cpf.nr_ddd_celular,
               cpf.nr_telefone_celular,
               pf.nr_ddi_celular nr_ddi_celular_principal,
               pf.nr_ddd_celular nr_ddd_celular_principal,
               pf.nr_telefone_celular nr_telefone_celular_principal,
               case when cpf.ie_mala_direta = 'S' then 'Sim' when cpf.ie_mala_direta = 'N' then 'Não' else cpf.ie_mala_direta end ds_mala_direta,
               (Select distinct first_value(apu_sub.cd_setor_atendimento) over(order by apu_sub.nr_seq_interno desc)
                  from tasy.atend_paciente_unidade apu_sub
                 where 1 = 1
                   and apu_sub.nr_atendimento = ap.nr_atendimento
                   and ((apu_sub.ie_passagem_setor in ('N', 'L')) or
                       (apu_sub.cd_setor_atendimento in
                       (0 /*131, 537, 324, 325, 129, 469, 75, 387, 87392, 614*/)))
                   and nvl(apu_sub.dt_saida_unidade, sysdate) =
                       (select max(nvl(apu_max.dt_saida_unidade, sysdate))
                          from tasy.atend_paciente_unidade apu_max
                         where apu_sub.nr_atendimento = apu_max.nr_atendimento
                           and ((apu_max.ie_passagem_setor in ('N', 'L')) or
                               (apu_max.cd_setor_atendimento in
                               (0 /*131, 537, 324, 325, 129, 469, 75, 387, 87392, 614*/))))) cd_setor_atendimento
          from tasy.atendimento_paciente ap,
               tasy.pessoa_fisica        pf,
               tasy.compl_pessoa_fisica  cpf,
               tasy.sus_carater_internacao sci
         where 1 = 1
           and ap.cd_estabelecimento = 1
           and cpf.ie_tipo_complemento = 1
           and pf.dt_obito is null
           and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00', 'dd/mm/rrrr hh24:mi:ss') and  to_date('DATE_TO_REPLACE_END 23:59:59', 'dd/mm/rrrr hh24:mi:ss')
           and ap.dt_cancelamento is null
           and (ap.ie_tipo_atendimento = 1 or (ap.ie_tipo_atendimento <> 1 AND sci.ds_carater_internacao = 'URGENCIA'))
           and ap.ie_carater_inter_sus = sci.cd_carater_internacao
           and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
           and ap.cd_pessoa_fisica = cpf.cd_pessoa_fisica(+)
           and (cpf.ds_email is not null or cpf.nr_telefone is not null or
               cpf.ds_fone_adic is not null or
               cpf.nr_telefone_celular is not null)) base,
       tasy.setor_atendimento sa,
       (select ag.cd_estabelecimento,
               ac.dt_agenda dt_agenda_consulta,
               pf.cd_pessoa_fisica, 
               ac.ie_status_agenda,
               (select vd.ds_valor_dominio
                  from tasy.valor_dominio vd
                 where vd.cd_dominio = 83
                   and vd.vl_dominio = ac.ie_status_agenda) ds_status_agenda_consulta,
               ag.cd_tipo_agenda,
               (select vd.ds_valor_dominio
                  from tasy.valor_dominio vd
                 where vd.cd_dominio = 34
                   and vd.vl_dominio = ag.cd_tipo_agenda) ds_tipo_agenda_consulta
          from tasy.agenda_consulta      ac,
               tasy.pessoa_fisica        pf,
               tasy.agenda               ag,
               tasy.atendimento_paciente ap
         where AC.cd_pessoa_fisica = PF.CD_PESSOA_FISICA
           and ac.cd_agenda = ag.cd_agenda
           and ap.cd_pessoa_fisica = ac.cd_pessoa_fisica
           and ap.cd_estabelecimento = 1
           and pf.dt_obito is null
           and ac.dt_agenda > ap.dt_alta
           and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00', 'dd/mm/rrrr hh24:mi:ss') and  to_date('DATE_TO_REPLACE_END 23:59:59', 'dd/mm/rrrr hh24:mi:ss')
           and ap.dt_cancelamento is null
           and ac.ie_status_agenda <> 'C') con,
       (select agp.cd_pessoa_fisica cd_pessoa_fisica_exame,
               agp.hr_inicio dt_agenda_exame,
               (select ds_expressao ds
                  from tasy.valor_dominio_v
                 where cd_dominio = 83
                   and vl_dominio = agp.ie_status_agenda
                   and tasy.obter_se_exibe_status(vl_dominio,
                                                  tasy.obter_tipo_agenda(ag.cd_agenda),
                                                  ag.cd_estabelecimento) = 'S') ds_status_agenda_exame,
               substr(tasy.obter_descricao_procedimento(agp.cd_procedimento,
                                                        agp.ie_origem_proced),
                      1,
                      150) ds_procedimento
          from tasy.agenda               ag,
               tasy.agenda_paciente      agp,
               tasy.atendimento_paciente ap,
               tasy.pessoa_fisica     pf
         where 1 = 1
           and ag.cd_agenda = agp.cd_agenda
           and ag.cd_tipo_agenda = 2
           and ag.cd_estabelecimento = 1
           and agp.cd_pessoa_fisica = ap.cd_pessoa_fisica
           and agp.cd_pessoa_fisica = pf.cd_pessoa_fisica
           and agp.ie_status_agenda <> 'C'
           and ap.cd_estabelecimento = 1
           and pf.dt_obito is null
           and agp.hr_inicio > ap.dt_alta
           and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00', 'dd/mm/rrrr hh24:mi:ss') and to_date('DATE_TO_REPLACE_END 23:59:59', 'dd/mm/rrrr hh24:mi:ss')) exa
 where 1=1 
   and base.cd_setor_atendimento = sa.cd_setor_atendimento
   and (base.cd_pessoa_fisica = con.cd_pessoa_fisica(+) and base.dt_alta < con.dt_agenda_consulta(+))
   and (base.cd_pessoa_fisica = exa.cd_pessoa_fisica_exame(+) and base.dt_alta < exa.dt_agenda_exame(+)))
 where 1=1
 and nvl(min_dt_agenda_consulta, sysdate) = nvl(dt_agenda_consulta, sysdate)
 and nvl(min_dt_agenda_exame, sysdate) = nvl(dt_agenda_exame, sysdate)
 group by nr_atendimento,
       ds_tipo_atendimento,
       dt_nascimento,
       nm_social,
       nm_pessoa_fisica,
       dt_entrada,
       dt_alta,
       ds_motivo_alta,
       ds_email,
       nr_ddi_telefone,
       nr_ddd_telefone,
       nr_telefone,
       nr_ramal,
       nr_ddi_fone_adic,
       nr_ddd_fone_adic,
       ds_fone_adic,
       nr_ddi_celular,
       nr_ddd_celular,
       nr_telefone_celular,
       nr_ddi_celular_principal,
       nr_ddd_celular_principal,
       nr_telefone_celular_principal,
       ds_mala_direta,
       ds_classif_setor,
       dt_agenda_consulta,
       ds_status_agenda_consulta,
       ds_tipo_agenda_consulta,
       dt_agenda_exame,
       ds_status_agenda_exame,
       ds_procedimento
 
-- Resumo de Internação Médica
select ap.nr_atendimento,
       tc.ds_label,
       re.ds_resultado,
       case when instr(r.ds_utc,'T') <> 0 then to_date(r.ds_utc, 'dd/mm/rrrr"T"hh24:mi:ss') else to_date(r.ds_utc, 'dd/mm/rrrr hh24:mi:ss') end ds_utc
  from tasy.ehr_registro          r,
       tasy.ehr_reg_template      rt,
       tasy.ehr_reg_elemento      re,
       tasy.ehr_elemento          e,
       tasy.ehr_template_conteudo tc,
       tasy.atendimento_paciente  ap,
	   tasy.pessoa_fisica		  pf
 where r.nr_sequencia = rt.nr_seq_reg
   and rt.nr_sequencia = re.nr_seq_reg_template
   and e.nr_sequencia = re.nr_seq_elemento
   and e.nr_sequencia = tc.nr_seq_elemento
   and tc.nr_seq_template = rt.nr_seq_template
   and r.nr_atendimento = ap.nr_atendimento
   and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
   and tc.nr_seq_template = 100531
   and re.nr_seq_elemento in (469,
                              9000524,
                              9000550)
   and ap.cd_estabelecimento = 1
   and pf.dt_obito is null
   and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00','dd/mm/rrrr hh24:mi:ss') and to_date('DATE_TO_REPLACE_END 23:59:59','dd/mm/rrrr hh24:mi:ss')
   and ap.dt_cancelamento is null
   and r.dt_liberacao is not null
   and re.dt_liberacao is not null

-- Receita
select ap.nr_atendimento, mer.dt_receita, mer.dt_liberacao, mer.ds_receita
  from tasy.atendimento_paciente ap,
       tasy.pessoa_fisica        pf,
       tasy.med_receita          mer
 where 1 = 1
   and ap.cd_estabelecimento = 1
   and pf.dt_obito is null
   and trunc(mer.dt_receita) >= trunc(ap.dt_alta)-3
   and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00','dd/mm/rrrr hh24:mi:ss') and to_date('DATE_TO_REPLACE_END 23:59:59','dd/mm/rrrr hh24:mi:ss')
   and ap.dt_cancelamento is null
   and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
   and ap.nr_atendimento = mer.nr_atendimento_hosp
   and mer.dt_liberacao is not null

-- Atestado
select ap.nr_atendimento, ate.dt_atestado, ate.dt_liberacao, ate.ds_atestado
  from tasy.atendimento_paciente ap,
       tasy.pessoa_fisica        pf,
       tasy.atestado_paciente    ate
 where 1 = 1
   and ap.cd_estabelecimento = 1
   and pf.dt_obito is null
   and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00','dd/mm/rrrr hh24:mi:ss') and to_date('DATE_TO_REPLACE_END 23:59:59','dd/mm/rrrr hh24:mi:ss')
   and ap.dt_cancelamento is null
   and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
   and ap.nr_atendimento = ate.nr_atendimento
   and ate.dt_liberacao is not null

-- Evolução Médica
select evp.nr_atendimento,
       evp.dt_evolucao,
       evp.dt_liberacao,
       evp.ds_evolucao
  from tasy.evolucao_paciente evp,
       tasy.pessoa_fisica        pf,
       tasy.atendimento_paciente ap
 where 1=1 
   and evp.nr_atendimento = ap.nr_atendimento
   and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
   and ap.cd_estabelecimento = 1
   and pf.dt_obito is null
   and ap.dt_cancelamento is null
   and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00','dd/mm/rrrr hh24:mi:ss') and to_date('DATE_TO_REPLACE_END 23:59:59','dd/mm/rrrr hh24:mi:ss')
   and evp.dt_liberacao is not null
   and evp.dt_inativacao is null
   and evp.ie_tipo_evolucao = '1'
   
-- Avaliação Médica PA Template
select ap.nr_atendimento,
       /* tc.ds_label, */
       re.ds_resultado,
	   case when instr(r.ds_utc,'T') <> 0 then to_date(r.ds_utc, 'dd/mm/rrrr"T"hh24:mi:ss') else to_date(r.ds_utc, 'dd/mm/rrrr hh24:mi:ss') end ds_utc
  from tasy.ehr_registro          r,
       tasy.ehr_reg_template      rt,
       tasy.ehr_reg_elemento      re,
       tasy.ehr_elemento          e,
       tasy.ehr_template_conteudo tc,
       tasy.atendimento_paciente  ap,
       tasy.pessoa_fisica      pf
 where r.nr_sequencia = rt.nr_seq_reg
   and rt.nr_sequencia = re.nr_seq_reg_template
   and e.nr_sequencia = re.nr_seq_elemento
   and e.nr_sequencia = tc.nr_seq_elemento   
   and tc.nr_seq_template = rt.nr_seq_template
   and r.nr_atendimento = ap.nr_atendimento
   and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
   and re.nr_seq_temp_conteudo = tc.nr_sequencia
   and tc.nr_seq_template in (100512,100517)
   and re.nr_seq_elemento = 9003836
   and ap.cd_estabelecimento = 1
   and pf.dt_obito is null
   and tc.ie_obrigatorio = 'S'
   and ap.dt_alta between to_date('DATE_TO_REPLACE_START 00:00:00','dd/mm/rrrr hh24:mi:ss') and to_date('DATE_TO_REPLACE_END 23:59:59','dd/mm/rrrr hh24:mi:ss')
   and ap.dt_cancelamento is null
   and r.dt_liberacao is not null
   and re.dt_liberacao is not null