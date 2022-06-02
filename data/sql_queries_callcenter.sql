-- Base
select nr_atendimento,
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
       ds_classif_setor,
       dt_agenda_consulta,
       ds_status_agenda_consulta,
       ds_tipo_agenda_consulta,
       dt_agenda_exame,
       ds_status_agenda_exame,
       ds_procedimento
  from (select base.nr_atendimento,
       base.dt_nascimento,
       base.nm_social,
       base.nm_pessoa_fisica,
       --base.ds_tipo_atendimento,
       base.dt_entrada,
       base.dt_alta,
       base.ds_motivo_alta,
       --base.tipo_contato,
       --base.nm_contato,
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
       --base.cd_setor_atendimento,
       (select vd.ds_valor_dominio
          from tasy.valor_dominio vd
         where vd.cd_dominio = 1
           and vd.vl_dominio = sa.cd_classif_setor) ds_classif_setor,
       --sa.ds_setor_atendimento,
       min(con.dt_agenda_consulta) over(partition by base.cd_pessoa_fisica) min_dt_agenda_consulta,
       con.*,
       min(exa.dt_agenda_exame) over(partition by base.cd_pessoa_fisica) min_dt_agenda_exame,
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
               tasy.compl_pessoa_fisica  cpf
         where 1 = 1
           and ap.cd_estabelecimento = 1
           and ap.ie_tipo_atendimento = 1
           and cpf.ie_tipo_complemento = 1
           and ap.cd_motivo_alta <> 7 -- Óbito
              --and ap.ie_tipo_atendimento in (1,3,7)
              --and ap.dt_entrada >= to_date('01/01/2016','dd/mm/rrrr')
           and trunc(ap.dt_alta) between to_date('DATE_TO_REPLACE_START', 'dd/mm/rrrr') and
               to_date('DATE_TO_REPLACE_END', 'dd/mm/rrrr')
           and ap.dt_cancelamento is null
           and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
           and ap.cd_pessoa_fisica = cpf.cd_pessoa_fisica(+)
           --and ap.CD_PESSOA_FISICA = 737213
           --and ap.nr_atendimento = 4051720
           and (cpf.ds_email is not null or cpf.nr_telefone is not null or
               cpf.ds_fone_adic is not null or
               cpf.nr_telefone_celular is not null)) base,
       tasy.setor_atendimento sa,
       (select ag.cd_estabelecimento,
               ac.dt_agenda dt_agenda_consulta,
               pf.cd_pessoa_fisica,
               --pf.nm_pessoa_fisica,  
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
           and ap.ie_tipo_atendimento = 1
           and ap.cd_motivo_alta <> 7 -- Óbito
           and trunc(ap.dt_alta) between to_date('DATE_TO_REPLACE_START', 'dd/mm/rrrr') and
               to_date('DATE_TO_REPLACE_END', 'dd/mm/rrrr')
           and ap.dt_cancelamento is null
           and ac.ie_status_agenda <> 'C') con,
       (select agp.cd_pessoa_fisica cd_pessoa_fisica_exame,
               --ag.ds_agenda,
               agp.hr_inicio dt_agenda_exame,
               --agp.ie_status_agenda,
               (select ds_expressao ds
                  from tasy.valor_dominio_v
                 where cd_dominio = 83
                   and vl_dominio = agp.ie_status_agenda
                   and tasy.obter_se_exibe_status(vl_dominio,
                                                  tasy.obter_tipo_agenda(ag.cd_agenda),
                                                  ag.cd_estabelecimento) = 'S') ds_status_agenda_exame,
               --agp.cd_medico,
               --substr(tasy.obter_nome_pf(agp.cd_medico), 1, 200) nm_medico,
               --agp.cd_procedimento,
               --agp.ie_origem_proced,
               --agp.nr_seq_proc_interno,
               substr(tasy.obter_descricao_procedimento(agp.cd_procedimento,
                                                        agp.ie_origem_proced),
                      1,
                      150) ds_procedimento /*,
               (select ds_proc_exame
                  from tasy.proc_interno
                 where nr_sequencia = agp.nr_seq_proc_interno) ds_proc_interno*/
          from tasy.agenda               ag,
               tasy.agenda_paciente      agp,
               tasy.atendimento_paciente ap
         where 1 = 1
           and ag.cd_agenda = agp.cd_agenda
           and ag.cd_tipo_agenda = 2 --exames
           and ag.cd_estabelecimento = 1
           and agp.cd_pessoa_fisica = ap.cd_pessoa_fisica
           and agp.ie_status_agenda <> 'C'
           and ap.cd_estabelecimento = 1
           and ap.ie_tipo_atendimento = 1
           and ap.cd_motivo_alta <> 7 --Óbito
           and trunc(ap.dt_alta) between to_date('DATE_TO_REPLACE_START', 'dd/mm/rrrr') and to_date('DATE_TO_REPLACE_END', 'dd/mm/rrrr')) exa
 where 1=1 
   and base.cd_setor_atendimento = sa.cd_setor_atendimento
   and (base.cd_pessoa_fisica = con.cd_pessoa_fisica(+) and base.dt_alta < con.dt_agenda_consulta(+))
   and (base.cd_pessoa_fisica = exa.cd_pessoa_fisica_exame(+) and base.dt_alta < exa.dt_agenda_exame(+)))
 where nvl(min_dt_agenda_consulta, sysdate) = nvl(dt_agenda_consulta, sysdate)
 and nvl(min_dt_agenda_exame, sysdate) = nvl(dt_agenda_exame, sysdate)
 order by 1


-- Orientação de Alta
select ap.nr_atendimento,
       tc.ds_label,
       re.ds_resultado,
       --m.nm_guerra medico,
       to_date(r.ds_utc, 'dd/mm/rrrr"T"hh24:mi:ss') ds_utc
  from tasy.ehr_registro          r,
       tasy.ehr_reg_template      rt,
       tasy.ehr_reg_elemento      re,
       tasy.ehr_elemento          e,
       tasy.ehr_template_conteudo tc,
       tasy.atendimento_paciente  ap
       --tasy.medico                m
 where r.nr_sequencia = rt.nr_seq_reg
   and rt.nr_sequencia = re.nr_seq_reg_template
   and e.nr_sequencia = re.nr_seq_elemento
   and e.nr_sequencia = tc.nr_seq_elemento
   and tc.nr_seq_template = rt.nr_seq_template
   and r.nr_atendimento = ap.nr_atendimento
   --and r.cd_profissional = m.cd_pessoa_fisica(+)
   and tc.nr_seq_template = 100531 --Resumo de Internação Médica [HTML]
   and re.nr_seq_elemento in (469, --Observações
                              9000524, --Outros
                              9000550) --Retorno médico em
   --and ap.nr_atendimento = 4071177
   and ap.cd_estabelecimento = 1
   and ap.ie_tipo_atendimento = 1
   and ap.cd_motivo_alta <> 7 --Óbito
   and trunc(ap.dt_alta) between to_date('DATE_TO_REPLACE_START','dd/mm/rrrr') and to_date('DATE_TO_REPLACE_END','dd/mm/rrrr')
   and ap.dt_cancelamento is null
   and r.dt_liberacao is not null
   and re.dt_liberacao is not null
 order by ap.nr_atendimento, tc.ds_label

-- Receita
select ap.nr_atendimento, mer.dt_receita, mer.dt_liberacao, mer.ds_receita
  from tasy.atendimento_paciente ap,
       tasy.pessoa_fisica        pf,
       tasy.med_receita          mer
 where 1 = 1
   and ap.cd_estabelecimento = 1
   and ap.ie_tipo_atendimento = 1
   and ap.cd_motivo_alta <> 7 --Óbito
   and trunc(ap.dt_alta) between to_date('DATE_TO_REPLACE_START','dd/mm/rrrr') and to_date('DATE_TO_REPLACE_END','dd/mm/rrrr')
   and ap.dt_cancelamento is null
   and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
   and ap.nr_atendimento = mer.nr_atendimento_hosp
   and mer.dt_liberacao is not null
 order by 1, 2

-- Atestados
select ap.nr_atendimento, ate.dt_atestado, ate.dt_liberacao, ate.ds_atestado
  from tasy.atendimento_paciente ap,
       tasy.pessoa_fisica        pf,
       tasy.atestado_paciente    ate
 where 1 = 1
   and ap.cd_estabelecimento = 1
   and ap.ie_tipo_atendimento = 1
   and ap.cd_motivo_alta <> 7 --Óbito
   and trunc(ap.dt_alta) between to_date('DATE_TO_REPLACE_START','dd/mm/rrrr') and to_date('DATE_TO_REPLACE_END','dd/mm/rrrr')
   and ap.dt_cancelamento is null
   and ap.cd_pessoa_fisica = pf.cd_pessoa_fisica
   and ap.nr_atendimento = ate.nr_atendimento
   and ate.dt_liberacao is not null
 order by 1, 2

