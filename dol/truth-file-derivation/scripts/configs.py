"""Per-protocol settings for build_truth.py (what the dissector output does not decide)."""


def at(r, name):
    """Payload offset of the first dissector field with this name, or None."""
    for n, o, w in r['fields']:
        if n == name:
            return o
    return None


def byte(r, p, name):
    o = at(r, name)
    return p[o] if o is not None and o < len(p) else None


def pairs(ids, req_suffix='_request', resp_suffix='_response', what='request'):
    """request/response pairs whose ids differ only in the suffix."""
    out = []
    for i in sorted(ids):
        if i.endswith(req_suffix):
            j = i[: -len(req_suffix)] + resp_suffix
            if j in ids:
                out.append((i, j, f'The {what} is answered by the matching response.'))
    return out


# ---------------------------------------------------------------- IEC 60870-5-104
IEC_TYPES = {1: 'm_sp_na_1', 3: 'm_dp_na_1', 5: 'm_st_na_1', 7: 'm_bo_na_1', 9: 'm_me_na_1', 11: 'm_me_nb_1',
             13: 'm_me_nc_1', 15: 'm_it_na_1', 30: 'm_sp_tb_1', 31: 'm_dp_tb_1', 34: 'm_me_td_1', 35: 'm_me_te_1',
             36: 'm_me_tf_1', 45: 'c_sc_na_1', 46: 'c_dc_na_1', 47: 'c_rc_na_1', 48: 'c_se_na_1', 49: 'c_se_nb_1',
             50: 'c_se_nc_1', 58: 'c_sc_ta_1', 59: 'c_dc_ta_1', 63: 'c_se_tc_1', 70: 'm_ei_na_1', 100: 'c_ic_na_1',
             101: 'c_ci_na_1', 102: 'c_rd_na_1', 103: 'c_cs_na_1', 105: 'c_rp_na_1', 107: 'c_ts_ta_1'}
IEC_U = {0x07: 'startdt_act', 0x0B: 'startdt_con', 0x13: 'stopdt_act', 0x23: 'stopdt_con', 0x43: 'testfr_act', 0x83: 'testfr_con'}


def iec104_key(r, p):
    if len(p) < 6:
        return None
    c = p[2]
    if c & 1 == 0:
        if len(p) < 7:
            return None
        t = p[6]
        name = IEC_TYPES.get(t, f'type{t}')
        if t >= 45:  # control direction: command and its (mirrored) confirmation
            role = 'request' if r['dir'] == 'client_to_server' else 'response'
            return f'iec104_{name}_{role}', role
        return f'iec104_{name}', 'notification'
    if c & 3 == 1:
        return 'iec104_s_format_ack', 'control'
    return f'iec104_u_format_{IEC_U.get(c, hex(c))}', 'control'


def iec104_relations(ids):
    out = pairs(ids, what='command (activation)')
    for a, b in (('startdt_act', 'startdt_con'), ('stopdt_act', 'stopdt_con'), ('testfr_act', 'testfr_con')):
        if f'iec104_u_format_{a}' in ids and f'iec104_u_format_{b}' in ids:
            out.append((f'iec104_u_format_{a}', f'iec104_u_format_{b}', f'U-format {a} is confirmed by {b}.'))
    return out


# ---------------------------------------------------------------- EtherCAT
ECAT_CMD = {0: 'nop', 1: 'aprd', 2: 'apwr', 3: 'aprw', 4: 'fprd', 5: 'fpwr', 6: 'fprw', 7: 'brd', 8: 'bwr', 9: 'brw',
            10: 'lrd', 11: 'lwr', 12: 'lrw', 13: 'armw', 14: 'frmw'}

# ---------------------------------------------------------------- HART-IP
HART_MSG = {0: 'session_initiate', 1: 'session_close', 2: 'keep_alive', 3: 'pass_through', 4: 'direct_pdu', 5: 'read_audit_log'}
HART_TYPE = {0: 'request', 1: 'response', 2: 'publish', 3: 'error', 15: 'nak'}


def hart_key(r, p):
    if len(p) < 8:
        return None
    mid, mtype = HART_MSG.get(p[2], f'msg{p[2]}'), HART_TYPE.get(p[1], f'type{p[1]}')
    cmd = byte(r, p, 'hart_ip.pt.command')
    name = f'hart_ip_{mid}' + (f'_cmd{cmd}' if cmd is not None else '') + f'_{mtype}'
    role = {'request': 'request', 'response': 'response', 'publish': 'notification'}.get(mtype, 'response')
    return name, role


# ---------------------------------------------------------------- EtherNet/IP and CIP
ENIP_CMD = {0x0004: 'list_services', 0x0063: 'list_identity', 0x0064: 'list_interfaces', 0x0065: 'register_session',
            0x0066: 'unregister_session', 0x006F: 'send_rr_data', 0x0070: 'send_unit_data'}
CIP_SVC = {0x01: 'get_attributes_all', 0x02: 'set_attributes_all', 0x03: 'get_attribute_list', 0x04: 'set_attribute_list',
           0x05: 'reset', 0x0A: 'multiple_service_packet', 0x0E: 'get_attribute_single', 0x10: 'set_attribute_single',
           0x4B: 'execute_pccc', 0x4C: 'read_tag', 0x4D: 'write_tag', 0x4E: 'forward_close', 0x52: 'unconnected_send',
           0x54: 'forward_open', 0x55: 'get_connection_data', 0x5B: 'large_forward_open', 0x4F: 'read_modify_write'}
ENIP_HEADER = {'command': {'semantic_role': 'function_code'}, 'length': {'semantic_role': 'length'},
               'session': {'name': 'session_handle', 'semantic_role': 'unit_id'}, 'status': {'semantic_role': 'status'},
               'context': {'name': 'sender_context', 'semantic_role': 'transaction_id'}, 'options': {'semantic_role': 'flags'}}


def is_cip_io(r):
    """Class 0/1 implicit I/O over UDP/2222: common packet format items, no encapsulation header."""
    return at(r, 'enip.command') is None and at(r, 'enip.cpf.itemcount') == 0


def enip_key(r, p, with_cip):
    if is_cip_io(r):
        return f'{"cip" if with_cip else "enip"}_class1_io', 'notification'
    if len(p) < 24:
        return None
    cmd = p[0] | p[1] << 8
    name = ENIP_CMD.get(cmd, f'cmd{cmd:#06x}')
    svc = byte(r, p, 'cip.service')
    if svc is not None:
        reply = bool(svc & 0x80)
        role = 'response' if reply else 'request'
        if with_cip:
            return f'cip_{name}_{CIP_SVC.get(svc & 0x7F, f"svc{svc & 0x7F:#04x}")}_{role}', role
        return f'enip_{name}_{role}', role
    if cmd in (0x0063, 0x0004, 0x0064):  # list requests carry no data
        role = 'request' if (p[2] | p[3] << 8) == 0 else 'response'
    elif r['dir'] in ('client_to_server', 'server_to_client'):
        role = 'request' if r['dir'] == 'client_to_server' else 'response'
    else:
        role = 'request' if (p[8] | p[9] << 8 | p[10] << 16 | p[11] << 24) == 0 and cmd == 0x65 and not p[4:8].strip(b'\0') else 'response'
    return f'{"cip" if with_cip else "enip"}_{name}_{role}', role


# ---------------------------------------------------------------- S7comm
S7_FUNC = {0x00: 'cpu_services', 0x04: 'read_var', 0x05: 'write_var', 0x1A: 'request_download', 0x1B: 'download_block',
           0x1C: 'download_ended', 0x1D: 'start_upload', 0x1E: 'upload', 0x1F: 'end_upload', 0x28: 'plc_control',
           0x29: 'plc_stop', 0xF0: 'setup_communication'}
S7_UD_GROUP = {1: 'mode_transition', 2: 'cyclic_data', 3: 'block_functions', 4: 'cpu_functions', 5: 'security',
               6: 'pbc', 7: 'time_functions'}


def s7_key(r, p):
    if len(p) < 19 or p[7] != 0x32:
        return None
    rosctr = p[8]
    if rosctr in (1, 3):
        o = at(r, 's7comm.param.func')
        if o is None:
            return None
        f = S7_FUNC.get(p[o], f'func{p[o]:#04x}')
        return (f's7comm_job_{f}', 'request') if rosctr == 1 else (f's7comm_ack_data_{f}', 'response')
    if rosctr == 7:
        o = at(r, 's7comm.param.userdata.funcgroup')
        s = byte(r, p, 's7comm.param.userdata.subfunc')
        if o is None:
            return None
        kind = 'request' if p[o] >> 4 == 4 else 'response'
        return f's7comm_userdata_{S7_UD_GROUP.get(p[o] & 15, p[o] & 15)}_sub{s}_{kind}', kind
    if rosctr == 2:
        return 's7comm_ack', 'response'
    return None


def s7_relations(ids):
    out = []
    for i in sorted(ids):
        if i.startswith('s7comm_job_') and 's7comm_ack_data_' + i[len('s7comm_job_'):] in ids:
            out.append((i, 's7comm_ack_data_' + i[len('s7comm_job_'):], 'A job is answered by ack-data with the same PDU reference.'))
    return out + pairs(ids, what='userdata request')


TPKT_COTP = ('TPKT (RFC 1006) and COTP data TPDU header carried on TCP port 102: version, reserved, length, '
             'COTP length indicator, PDU type, TPDU number / EOT.')
TPKT_HEADER = {'version': {'semantic_role': 'constant'}, 'reserved': {'semantic_role': 'reserved'},
               'length': {'name': 'tpkt_length', 'semantic_role': 'length'}, 'li': {'name': 'cotp_length_indicator', 'semantic_role': 'length'},
               'type': {'name': 'cotp_pdu_type', 'semantic_role': 'constant'}, 'eot': {'name': 'cotp_tpdu_number', 'semantic_role': 'flags'}}

CONFIGS = {
    'iec104': dict(
        protocol_name='IEC 60870-5-104', version='IEC 60870-5-104:2006', header_len=6, endian='little',
        strip=['iec60870_104.', 'iec60870_asdu.'], rename={'rx': 'control_field', 'tx': 'control_field', 'type': 'control_field', 'utype': 'control_field'},
        prefer=['typeid', 'causetx', 'numix', 'ioa'],
        roles={'start': 'constant', 'apdulen': 'length', 'control_field': 'sequence_number', 'typeid': 'function_code',
               'causetx': 'status', 'numix': 'quantity', 'oa': 'address', 'addr': 'address', 'ioa': 'address'},
        drop=[r'\.(sco|dco|rco|qos|siq|diq|qds|qoi|qcc|vti|bcr|cp56time|cp24time|qpm|scs)\.', r'\.(nega|test|sq)$'],
        header_name='IEC 104 APCI', header_description='Application Protocol Control Information: start byte 0x68, APDU length, four control octets (I-, S- or U-format).',
        key=iec104_key, disc=lambda tid: not tid.startswith(('iec104_s_', 'iec104_u_')), disc_name='type_identification',
        relations=iec104_relations,
        description='IEC 60870-5-104 telecontrol over TCP/2404. Every APDU starts with the 6-byte APCI; I-format APDUs carry an ASDU whose first octet (type identification) selects the message type.',
        offset_convention='APCI fields use wire-absolute offsets 0..5; ASDU types are relative to the ASDU (offset 0 = type identification = wire offset 6).'),
    'ethercat': dict(
        protocol_name='EtherCAT', version='ETG.1000', header_len=2, endian='little',
        strip=['ecatf.', 'ecat.'], prefer=['length', 'cmd', 'idx', 'adp', 'ado', 'int', 'cnt'],
        rename={'ecatf': 'frame_header', 'length': 'frame_header', 'type': 'frame_header', 'reserved': 'frame_header',
                'circulating': 'datagram_length', 'more': 'datagram_length', 'subframe_length': 'datagram_length',
                'subframe_circulating': 'datagram_length', 'subframe_more': 'datagram_length', 'subframe_reserved': 'datagram_length',
                'cmd': 'command', 'idx': 'index', 'adp': 'address_position', 'ado': 'address_offset', 'int': 'irq', 'cnt': 'working_counter'},
        roles={'frame_header': 'length', 'command': 'function_code', 'index': 'transaction_id', 'address_position': 'address',
               'address_offset': 'address', 'datagram_length': 'length', 'irq': 'flags', 'working_counter': 'counter'},
        drop=[r'^ecat\.(reg|sii|fmmu|syncman|dc)', r'^ecat_mailbox', r'^ecatf\.'],
        header_name='EtherCAT frame header', header_description='11-bit frame length, reserved bit and 4-bit type (1 = datagrams).',
        key=lambda r, p: (f'ethercat_{ECAT_CMD.get(p[2], p[2])}_frame', 'request') if len(p) > 2 else None,
        disc=True, disc_name='command', relations=lambda ids: [],
        description='EtherCAT frames (EtherType 0x88A4) of datagrams sent by the master and returned by the slaves; the first datagram command selects the message type. Datagram data is the addressed slave memory / process image and is one bytes field.',
        offset_convention='The 2-byte frame header uses wire-absolute offsets; datagram types are relative to the first datagram (offset 0 = command = wire offset 2).'),
    'hart_ip': dict(
        protocol_name='HART-IP', version='HCF_SPEC-085', header_len=8, endian='big',
        strip=['hart_ip.pt.rsp.', 'hart_ip.pt.req.', 'hart_ip.pt.', 'hart_ip.session_init.', 'hart_ip.'],
        prefer=['^delimiter$', 'command', 'length', 'response_code', 'device_status'],
        rename={'transaction_id': 'sequence_number'},
        roles={'version': 'constant', 'message_type': 'function_code', 'message_id': 'function_code', 'status': 'status',
               'sequence_number': 'sequence_number', 'msg_length': 'length', 'delimiter': 'flags', 'long_address': 'address',
               'command': 'function_code', 'length': 'byte_count', 'checksum': 'checksum'},
        header_name='HART-IP header', header_description='Version, message type, message id, status, sequence number and message length.',
        key=hart_key, disc=False, relations=pairs,
        description='HART-IP (TCP/UDP 5094). The 8-byte header is followed by the message body; pass-through messages carry a HART PDU whose command selects the type.',
        offset_convention='Header fields use wire-absolute offsets 0..7; body types are relative to the body (offset 0 = wire offset 8).'),
    'enip': dict(
        protocol_name='EtherNet/IP encapsulation', version='CIP Vol. 2', header_len=24, endian='little',
        strip=['enip.', 'cip.'], header_overrides=ENIP_HEADER, prefer=['typeid', 'length', 'itemcount'],
        drop=[r'^cip\.'],
        roles={'sud_iface': 'unit_id', 'srrd_iface': 'unit_id', 'timeout': 'quantity', 'cpf_itemcount': 'quantity',
               'cpf_typeid': 'function_code', 'cpf_length': 'length', 'connid': 'unit_id', 'cpf_cai_connid': 'unit_id',
               'encapver': 'constant', 'sinfamily': 'constant', 'sinport': 'address', 'sinaddr': 'address'},
        header_name='EtherNet/IP encapsulation header', header_description='Command, length, session handle, status, sender context and options.',
        key=lambda r, p: enip_key(r, p, False), disc=False, relations=pairs,
        pdu_lo=lambda r: 0 if is_cip_io(r) else 24,
        description='EtherNet/IP encapsulation (TCP/UDP 44818). The 24-byte encapsulation header is followed by command-specific data (common packet format items); the encapsulated CIP message is one bytes field here.',
        offset_convention='Encapsulation header fields use wire-absolute offsets 0..23; command data types are relative to offset 24. Class-1 I/O frames (UDP/2222) carry no encapsulation header: enip_class1_io offsets start at the UDP payload.'),
    'cip': dict(
        protocol_name='CIP over EtherNet/IP', version='CIP Vol. 1/2', header_len=24, endian='little',
        strip=['enip.', 'cip.'], header_overrides=ENIP_HEADER,
        prefer=['^service$', 'typeid', 'length', 'itemcount', 'request_path_size'],
        rename={'rr': 'service', 'sc': 'service', 'cm_sc': 'service', 'logical_segment_format': 'path_segment',
                'logical_segment_type': 'path_segment', 'path_segment_type': 'path_segment', 'data_segment_type': 'path_segment'},
        roles={'service': 'function_code', 'request_path_size': 'length', 'genstat': 'status', 'addstat_size': 'length',
               'seq': 'sequence_number', 'cpf_typeid': 'function_code', 'cpf_length': 'length', 'cpf_itemcount': 'quantity',
               'sud_iface': 'unit_id', 'srrd_iface': 'unit_id', 'timeout': 'quantity', 'connid': 'unit_id',
               'path_segment': 'flags', 'class': 'address', 'instance': 'address', 'attribute': 'address'},
        header_name='EtherNet/IP encapsulation header', header_description='Command, length, session handle, status, sender context and options.',
        key=lambda r, p: enip_key(r, p, True), disc=False, relations=pairs,
        description='CIP explicit messages carried in EtherNet/IP SendRRData / SendUnitData; the CIP service code (with the reply bit) selects the message type.',
        offset_convention='Encapsulation header fields use wire-absolute offsets 0..23; CIP message types are relative to offset 24 (interface handle, timeout, common packet format items, then the CIP message).'),
    's7comm': dict(
        protocol_name='S7comm', version='S7comm (ISO-on-TCP)', header_len=7, endian='big',
        strip=['s7comm.', 'tpkt.', 'cotp.'], header_overrides=TPKT_HEADER, prefer=['^header_rosctr', 'func', 'itemcount', 'length'],
        roles={'header_protid': 'constant', 'header_rosctr': 'function_code', 'header_redid': 'reserved', 'header_pduref': 'transaction_id',
               'header_parlg': 'length', 'header_datlg': 'length', 'header_errcls': 'status', 'header_errcod': 'status',
               'param_func': 'function_code', 'param_itemcount': 'quantity', 'param_item_varspec': 'constant',
               'param_item_varspec_length': 'length', 'param_item_syntaxid': 'constant', 'param_item_transp_size': 'flags',
               'param_item_length': 'quantity', 'param_item_db': 'address', 'param_item_area': 'address', 'param_item_address': 'address',
               'data_returncode': 'status', 'data_transportsize': 'flags', 'data_length': 'length',
               'param_userdata_funcgroup': 'function_code', 'param_userdata_subfunc': 'function_code', 'param_userdata_seq_num': 'sequence_number',
               'param_errcod': 'status'},
        header_name='TPKT/COTP header', header_description=TPKT_COTP,
        key=s7_key, disc=False, relations=s7_relations,
        description='Siemens S7comm over ISO-on-TCP (TCP/102). After TPKT/COTP, the S7 header (protocol id 0x32, ROSCTR, PDU reference, parameter and data lengths) is followed by the parameter block whose function code selects the message type.',
        offset_convention='TPKT/COTP fields use wire-absolute offsets 0..6; S7 types are relative to the S7 header (offset 0 = protocol id 0x32 = wire offset 7).'),
}


# ---------------------------------------------------------------- DNP3
# The dissector reports application-layer offsets in its reassembled (CRC-stripped)
# buffer, not on the wire, so DNP3 frames are parsed here: link header, the 16-byte
# data blocks with their CRCs, transport and application headers, first object header.
DNP3_FC = {0: 'confirm', 1: 'read', 2: 'write', 3: 'select', 4: 'operate', 5: 'direct_operate', 6: 'direct_operate_nr',
           7: 'immediate_freeze', 9: 'freeze_clear', 13: 'cold_restart', 14: 'warm_restart', 20: 'enable_unsolicited',
           21: 'disable_unsolicited', 22: 'assign_class', 23: 'delay_measure', 24: 'record_current_time',
           129: 'response', 130: 'unsolicited_response'}
DNP3_LINK_PRM = {0: 'reset_link_states', 2: 'test_link_states', 3: 'confirmed_user_data', 4: 'unconfirmed_user_data', 9: 'request_link_status'}
DNP3_LINK_SEC = {0: 'ack', 1: 'nack', 11: 'link_status', 15: 'not_supported'}
DNP3_RANGE = {0x00: (1, 1), 0x01: (2, 2), 0x06: (), 0x07: (1,), 0x08: (2,), 0x17: (1,), 0x28: (2,), 0x5B: (2,)}


def dnp3_fields(p, r):
    f = [('start', 0, 2), ('length', 2, 1), ('control', 3, 1), ('destination', 4, 2), ('source', 6, 2), ('header_crc', 8, 2)]
    if len(p) <= 10:
        return f
    wire = lambda i: 10 + (i // 16) * 18 + i % 16
    data = bytearray()
    pos = 10
    while pos < len(p):
        block = p[pos:pos + 18]
        if len(block) <= 2:
            break
        data += block[:-2]
        f.append(('data_crc', pos + len(block) - 2, 2))
        pos += 18
    hdr = [('transport_control', 0, 1)]
    if len(data) >= 3:
        hdr += [('application_control', 1, 1), ('function_code', 2, 1)]
        s = 3
        if data[2] in (129, 130) and len(data) >= 5:
            hdr.append(('internal_indications', 3, 2))
            s = 5
        if len(data) >= s + 3:
            hdr += [('object_group', s, 1), ('object_variation', s + 1, 1), ('qualifier', s + 2, 1)]
            o = s + 3
            for k, w in enumerate(DNP3_RANGE.get(data[s + 2], ())):
                if o + w <= len(data):
                    hdr.append((('range_start', 'range_stop')[k] if len(DNP3_RANGE[data[s + 2]]) == 2 else 'count', o, w))
                o += w
    for n, o, w in hdr:
        if o // 16 == (o + w - 1) // 16:  # inside one data block
            f.append((n, wire(o), w))
    return f


def dnp3_key(r, p):
    if len(p) < 10 or p[:2] != b'\x05\x64':
        return None
    ctl = p[3]
    if p[2] == 5 or len(p) <= 12:
        if ctl & 0x40:
            return f'dnp3_link_{DNP3_LINK_PRM.get(ctl & 15, ctl & 15)}', 'request'
        return f'dnp3_link_{DNP3_LINK_SEC.get(ctl & 15, ctl & 15)}', 'response'
    fc = p[12]
    name = DNP3_FC.get(fc, f'fc{fc}')
    role = 'response' if fc in (0, 129) else 'notification' if fc == 130 else 'request'
    return f'dnp3_app_{name}', role


def dnp3_relations(ids):
    out = [(i, 'dnp3_app_response', 'The outstation answers the request with a solicited response (matching application sequence number).')
           for i in sorted(ids) if i.startswith('dnp3_app_') and i not in ('dnp3_app_response', 'dnp3_app_confirm', 'dnp3_app_unsolicited_response')
           and 'dnp3_app_response' in ids]
    if 'dnp3_app_unsolicited_response' in ids and 'dnp3_app_confirm' in ids:
        out.append(('dnp3_app_unsolicited_response', 'dnp3_app_confirm', 'An unsolicited response with CON set is confirmed by the master.'))
    for a, b in (('reset_link_states', 'ack'), ('test_link_states', 'ack'), ('request_link_status', 'link_status')):
        if f'dnp3_link_{a}' in ids and f'dnp3_link_{b}' in ids:
            out.append((f'dnp3_link_{a}', f'dnp3_link_{b}', f'Link-layer {a} is answered by {b}.'))
    return out


# ---------------------------------------------------------------- BACnet/IP
BAC_CONF = {0: 'acknowledge_alarm', 1: 'confirmed_cov_notification', 2: 'confirmed_event_notification', 3: 'get_alarm_summary',
            4: 'get_enrollment_summary', 5: 'subscribe_cov', 6: 'atomic_read_file', 7: 'atomic_write_file', 8: 'add_list_element',
            9: 'remove_list_element', 10: 'create_object', 11: 'delete_object', 12: 'read_property', 13: 'read_property_conditional',
            14: 'read_property_multiple', 15: 'write_property', 16: 'write_property_multiple', 17: 'device_communication_control',
            18: 'confirmed_private_transfer', 19: 'confirmed_text_message', 20: 'reinitialize_device', 26: 'read_range',
            28: 'subscribe_cov_property', 29: 'get_event_information'}
BAC_UNCONF = {0: 'i_am', 1: 'i_have', 2: 'unconfirmed_cov_notification', 3: 'unconfirmed_event_notification',
              4: 'unconfirmed_private_transfer', 5: 'unconfirmed_text_message', 6: 'time_synchronization', 7: 'who_has',
              8: 'who_is', 9: 'utc_time_synchronization', 10: 'write_group'}


def bacnet_key(r, p):
    o = at(r, 'bacapp.type')
    if o is None:
        return ('bacnet_network_layer_message', 'control') if at(r, 'bacnet.mesgtyp') is not None else None
    t = p[o] >> 4
    if t == 1:
        s = byte(r, p, 'bacapp.unconfirmed_service')
        return f'bacnet_{BAC_UNCONF.get(s, f"unconfirmed{s}")}', 'notification'
    if t in (4, 6, 7):
        return f'bacnet_{("", "", "", "", "segment_ack", "", "reject", "abort")[t]}', 'response'
    s = byte(r, p, 'bacapp.confirmed_service')
    name = BAC_CONF.get(s, f'service{s}')
    if t == 0:
        return f'bacnet_{name}_request', 'request'
    return f'bacnet_{name}_{"error" if t == 5 else "ack"}', 'response'


CONFIGS['dnp3'] = dict(
    protocol_name='DNP3', version='IEEE 1815-2012', header_len=10, endian='little', strip=[], fields_fn=dnp3_fields,
    roles={'start': 'constant', 'length': 'length', 'control': 'flags', 'destination': 'address', 'source': 'address',
           'header_crc': 'checksum', 'data_crc': 'checksum', 'transport_control': 'sequence_number', 'application_control': 'sequence_number',
           'function_code': 'function_code', 'internal_indications': 'status', 'object_group': 'opcode', 'object_variation': 'opcode',
           'qualifier': 'flags', 'range_start': 'address', 'range_stop': 'address', 'count': 'quantity'},
    header_name='DNP3 link-layer header', header_description='Start bytes 0x0564, length, link control, destination and source addresses, header CRC.',
    key=dnp3_key, disc=False, relations=dnp3_relations,
    description='DNP3 over TCP/UDP 20000. The 10-byte link header is followed by 16-byte user-data blocks each closed by a CRC; the first block starts with the transport header and the application header whose function code selects the message type (link-only frames are typed by the link function).',
    offset_convention='Link-header fields use wire-absolute offsets 0..9; the other types are relative to offset 10 (first data block). Offsets are wire offsets, i.e. the block CRCs are counted.')

CONFIGS['bacnet'] = dict(
    protocol_name='BACnet/IP', version='ANSI/ASHRAE 135', header_len=4, endian='big',
    strip=['bvlc.', 'bacnet.', 'bacapp.'], prefer=['^type$', 'confirmed_service', 'unconfirmed_service', 'invoke_id', 'control'],
    rename={'sa': 'type', 'more_segments': 'type', 'segmented_request': 'type', 'srv': 'type', 'nak': 'type',
            'der': 'control', 'dst': 'control', 'src': 'control', 'expect': 'control', 'prio': 'control', 'mesgtyp': 'message_type',
            'tag_class': 'tag', 'context_tag_number': 'tag', 'application_tag_number': 'tag', 'lvt': 'tag'},
    roles={'type': 'function_code', 'function': 'function_code', 'version': 'constant', 'control': 'flags', 'dnet': 'address',
           'dlen': 'length', 'dadr_eth': 'address', 'dadr_mstp': 'address', 'dadr_tmp': 'address', 'snet': 'address', 'slen': 'length',
           'sadr_mstp': 'address', 'sadr_eth': 'address', 'hopc': 'counter', 'max_adpu_size': 'flags', 'invoke_id': 'transaction_id',
           'confirmed_service': 'function_code', 'unconfirmed_service': 'function_code', 'sequence_number': 'sequence_number',
           'window_size': 'quantity', 'tag': 'flags', 'instance_number': 'address', 'object_type': 'address',
           'property_identifier': 'address'},
    header_overrides={'type': {'name': 'bvlc_type', 'semantic_role': 'constant'}, 'function': {'name': 'bvlc_function', 'semantic_role': 'function_code'},
                      'length': {'name': 'bvlc_length', 'semantic_role': 'length'}},
    header_name='BACnet Virtual Link Control', header_description='BVLC type 0x81, BVLC function and BVLC length.',
    key=bacnet_key, disc=False, relations=lambda ids: pairs(ids, '_request', '_ack', 'confirmed service request'),
    description='BACnet/IP (UDP 47808): BVLC header, NPDU (version, control and optional network addresses) and APDU; the APDU type and service choice select the message type. Tag-encoded service parameters have no fixed offsets and are one bytes field.',
    offset_convention='BVLC fields use wire-absolute offsets 0..3; the other types are relative to the NPDU (offset 0 = NPDU version = wire offset 4).')


# ---------------------------------------------------------------- ZigBee (ZEP encapsulation)
def zigbee_key(r, p):
    if len(p) < 50 or p[:2] != b'EX':
        return None
    nwk = p[41] & 3
    if nwk == 1:
        return 'zigbee_nwk_command', 'control'
    aps = p[49] & 3
    return {0: ('zigbee_aps_data', 'request'), 1: ('zigbee_aps_command', 'control'), 2: ('zigbee_aps_ack', 'response')}.get(aps)


CONFIGS['zigbee'] = dict(
    protocol_name='ZigBee (ZEP encapsulated)', version='ZigBee PRO / ZEP v2', header_len=32, endian='little',
    strip=['zep.', 'wpan.', 'zbee_nwk.', 'zbee_aps.', 'zbee_zcl.'], prefer=['ack_request', 'discovery', 'ack_req', 'ack_format'],
    rename={'ack_request': 'mac_frame_control', 'discovery': 'nwk_frame_control', 'ack_req': 'aps_frame_control', 'ack_format': 'aps_frame_control',
            'addr16': 'mac_address', 'addr': 'nwk_address', 'seq_no': 'mac_sequence_number', 'seqno': 'nwk_sequence_number',
            'fcs_ok': 'fcs', 'correlation': 'fcs', 'zbee_zcl': 'zcl_frame'},
    roles={'fcf': 'flags', 'protocol_id': 'constant', 'version': 'constant', 'type': 'function_code', 'channel_id': 'unit_id', 'device_id': 'unit_id',
           'lqi_mode': 'flags', 'lqi': 'status', 'time': 'timestamp', 'nwk_sequence_number': 'sequence_number', 'length': 'length',
           'mac_frame_control': 'flags', 'mac_sequence_number': 'sequence_number', 'dst_pan': 'address', 'mac_address': 'address',
           'nwk_frame_control': 'flags', 'nwk_address': 'address', 'radius': 'counter', 'aps_frame_control': 'flags',
           'dst': 'address', 'src': 'address', 'cluster': 'function_code', 'profile': 'constant', 'counter': 'counter', 'fcs': 'checksum'},
    header_overrides={'nwk_sequence_number': {'name': 'zep_sequence_number', 'semantic_role': 'sequence_number'}, 'bytes_21': {'name': 'reserved', 'semantic_role': 'reserved'}},
    header_name='ZEP header', header_description='ZigBee Encapsulation Protocol v2 data header (UDP 17754): preamble "EX", version, type, channel, device id, LQI mode, LQI, timestamp, sequence number, reserved bytes and the length of the encapsulated 802.15.4 frame.',
    key=zigbee_key, disc=False, relations=lambda ids: ([('zigbee_aps_data', 'zigbee_aps_ack', 'An APS data frame with acknowledge request is answered by an APS acknowledgement.')]
                                                        if {'zigbee_aps_data', 'zigbee_aps_ack'} <= ids else []),
    description='ZigBee frames carried in ZEP over UDP 17754: ZEP header, IEEE 802.15.4 MAC header, ZigBee NWK header and APS frame; the NWK and APS frame types select the message type.',
    offset_convention='ZEP fields use wire-absolute offsets 0..31; the other types are relative to the 802.15.4 frame (offset 0 = MAC frame control = wire offset 32).')


# ---------------------------------------------------------------- POWERLINK (EPL over UDP, ASnd SDO)
EPL_SDO = {0: 'nil', 1: 'write_by_index', 2: 'read_by_index', 3: 'write_all_by_index', 4: 'read_all_by_index',
           5: 'write_by_name', 6: 'read_by_name', 8: 'file_write', 9: 'file_read', 0x31: 'write_multiple_by_index', 0x32: 'read_multiple_by_index'}


def powerlink_fields(p, r):
    f = [x for x in r['fields'] if x[0] != 'epl.asnd' or x[2] == 1]
    return f + [('epl.dest', 1, 1), ('epl.src', 2, 1)]


def powerlink_key(r, p):
    if len(p) < 8 or p[0] != 0x06:
        return None
    if len(p) <= 8:
        return 'powerlink_sdo_sequence_layer', 'control'
    if len(p) < 12:
        return None
    flags, cmd = p[10], EPL_SDO.get(p[11], f'cmd{p[11]}')
    if flags & 0x40:
        return f'powerlink_sdo_{cmd}_abort', 'response'
    return (f'powerlink_sdo_{cmd}_response', 'response') if flags & 0x80 else (f'powerlink_sdo_{cmd}_request', 'request')


CONFIGS['powerlink'] = dict(
    protocol_name='Ethernet POWERLINK (ASnd over UDP)', version='EPSG DS 301', header_len=4, endian='little',
    strip=['epl.asnd.sdo.cmd.', 'epl.asnd.sdo.seq.', 'epl.asnd.', 'epl.od.', 'epl.'], fields_fn=powerlink_fields,
    rename={'asnd': 'message_type', 'mtyp': 'message_type', 'svid': 'service_id', 'receive_con': 'receive_sequence', 'send_con': 'send_sequence',
            'receive_sequence_number': 'receive_sequence', 'send_sequence_number': 'send_sequence'},
    prefer=['con$', 'abort$', 'command_id'],
    roles={'message_type': 'function_code', 'dest': 'address', 'src': 'address', 'service_id': 'function_code',
           'receive_sequence': 'sequence_number', 'send_sequence': 'sequence_number', 'transaction_id': 'transaction_id',
           'abort': 'flags', 'command_id': 'function_code', 'segment_size': 'length', 'data_index': 'address',
           'data_subindex': 'address', 'abort_code': 'error_code', 'data_uint': 'value'},
    header_name='POWERLINK ASnd header', header_description='Message type (0x06 = ASnd), destination node, source node and ASnd service id (0x05 = SDO).',
    key=powerlink_key, disc=False, relations=pairs,
    description='Ethernet POWERLINK asynchronous SDO transfers carried over UDP 3819: ASnd header, SDO sequence layer and SDO command layer whose command id and response/abort flags select the message type.',
    offset_convention='ASnd header fields use wire-absolute offsets 0..3; SDO types are relative to the sequence layer (offset 0 = wire offset 4).')


# ---------------------------------------------------------------- OPC UA binary
UA_SVC = {428: 'get_endpoints', 422: 'find_servers', 446: 'open_secure_channel', 452: 'close_secure_channel', 461: 'create_session',
          467: 'activate_session', 473: 'close_session', 527: 'browse', 533: 'browse_next', 554: 'translate_browse_paths',
          560: 'register_nodes', 566: 'unregister_nodes', 631: 'read', 664: 'history_read', 673: 'write', 712: 'call',
          751: 'create_monitored_items', 763: 'modify_monitored_items', 781: 'delete_monitored_items', 787: 'create_subscription',
          793: 'modify_subscription', 799: 'set_publishing_mode', 826: 'publish', 832: 'republish', 845: 'delete_subscriptions'}


def opcua_key(r, p):
    t = p[:3].decode('latin-1')
    if t == 'HEL':
        return 'opcua_hello', 'request'
    if t == 'ACK':
        return 'opcua_acknowledge', 'response'
    if t == 'ERR':
        return 'opcua_error', 'response'
    o = at(r, 'opcua.servicenodeid.numeric')
    sid = None
    if o is not None:
        w = next(w for n, oo, w in r['fields'] if n == 'opcua.servicenodeid.numeric' and oo == o)
        sid = int.from_bytes(p[o:o + w], 'little')
    if sid == 397:
        return 'opcua_service_fault', 'response'
    if sid is not None:
        if sid in UA_SVC:
            return f'opcua_{UA_SVC[sid]}_request', 'request'
        if sid - 3 in UA_SVC:
            return f'opcua_{UA_SVC[sid - 3]}_response', 'response'
        role = 'request' if r['dir'] == 'client_to_server' else 'response'
        return f'opcua_service{sid}_{role}', role
    role = 'request' if r['dir'] == 'client_to_server' else 'response'
    kind = {'OPN': 'open_secure_channel', 'CLO': 'close_secure_channel', 'MSG': 'encrypted_message'}.get(t, t.lower())
    return f'opcua_{kind}_{role}', role


CONFIGS['opcua'] = dict(
    protocol_name='OPC UA binary (UA TCP)', version='OPC 10000-6', header_len=8, endian='little',
    strip=['opcua.transport.', 'opcua.security.', 'opcua.'], prefer=['^type$', 'size'],
    roles={'type': 'function_code', 'chunk': 'flags', 'size': 'length', 'scid': 'unit_id', 'tokenid': 'unit_id', 'seq': 'sequence_number',
           'rqid': 'transaction_id', 'servicenodeid_encodingmask': 'flags', 'servicenodeid_nsid': 'constant', 'servicenodeid_numeric': 'function_code',
           'spu': 'payload', 'spul': 'length', 'scert': 'payload', 'scertl': 'length', 'rcthumb': 'payload', 'rcthumbl': 'length',
           'timestamp': 'timestamp', 'requesthandle': 'transaction_id', 'version': 'constant', 'rbs': 'length', 'sbs': 'length',
           'mms': 'length', 'mcc': 'quantity', 'endpointurl': 'payload'},
    header_overrides={'type': {'name': 'message_type', 'field_type': 'bytes'}, 'size': {'name': 'message_size'}},
    header_name='UA TCP message header', header_description='Three-byte ASCII message type (HEL, ACK, ERR, OPN, CLO, MSG), chunk type and message size.',
    key=opcua_key, disc=False, relations=pairs,
    description='OPC UA binary protocol over TCP 4840: UA TCP message header, then the secure-conversation headers and the encoded service request/response whose node id selects the message type. Encrypted message bodies are one bytes field.',
    offset_convention='Message header fields use wire-absolute offsets 0..7; the other types are relative to offset 8.')


# ---------------------------------------------------------------- MMS (ISO 9506) over ISO-on-TCP
MMS_PDU = {0xA0: 'confirmed_request', 0xA1: 'confirmed_response', 0xA2: 'confirmed_error', 0xA3: 'unconfirmed', 0xA4: 'reject',
           0xA5: 'cancel_request', 0xA6: 'cancel_response', 0xA8: 'initiate_request', 0xA9: 'initiate_response',
           0xAA: 'initiate_error', 0x8B: 'conclude_request', 0x8C: 'conclude_response', 0xAB: 'conclude_request', 0xAC: 'conclude_response'}
# ConfirmedServiceRequest / Response choice numbers (ISO 9506-2)
MMS_SVC = dict(enumerate('''status get_name_list identify rename read write get_variable_access_attributes define_named_variable define_scattered_access get_scattered_access_attributes delete_variable_access define_named_variable_list get_named_variable_list_attributes delete_named_variable_list define_named_type get_named_type_attributes delete_named_type input output take_control relinquish_control define_semaphore delete_semaphore report_semaphore_status report_pool_semaphore_status report_semaphore_entry_status initiate_download_sequence download_segment terminate_download_sequence initiate_upload_sequence upload_segment terminate_upload_sequence request_domain_download request_domain_upload load_domain_content store_domain_content delete_domain get_domain_attributes create_program_invocation delete_program_invocation start stop resume reset kill get_program_invocation_attributes obtain_file define_event_condition delete_event_condition get_event_condition_attributes report_event_condition_status alter_event_condition_monitoring trigger_event define_event_action delete_event_action get_event_action_attributes report_event_action_status define_event_enrollment delete_event_enrollment alter_event_enrollment report_event_enrollment_status get_event_enrollment_attributes acknowledge_event_notification get_alarm_summary get_alarm_enrollment_summary read_journal write_journal initialize_journal report_journal_status create_journal delete_journal get_capability_list file_open file_read file_close file_rename file_delete file_directory'''.split()))
MMS_UNCONF = {0: 'information_report', 1: 'unsolicited_status', 2: 'event_notification'}


def ber(p, o):
    """(tag number, constructed, header length, value length) of the BER TLV at o, or None."""
    if o + 2 > len(p):
        return None
    t, h = p[o], 1
    num = t & 0x1F
    if num == 0x1F:
        num = 0
        while o + h < len(p):
            num = num << 7 | p[o + h] & 0x7F
            h += 1
            if not p[o + h - 1] & 0x80:
                break
    if o + h >= len(p):
        return None
    L = p[o + h]
    h += 1
    if L & 0x80:
        n = L & 0x7F
        if n == 0 or o + h + n > len(p):
            return None
        L = int.from_bytes(p[o + h:o + h + n], 'big')
        h += n
    return num, bool(t & 0x20), h, L


def mms_start(p):
    """Offset of the first BER element after TPKT/COTP and the session header (data transfer SPDUs)."""
    if len(p) > 10 and p[7:11] == b'\x01\x00\x01\x00':
        return 11
    return 7


def mms_pdu(p):
    """Offset of the MMS PDU: unwrap presentation 0x61 / 0x30 / context id / single-ASN1-type [0]."""
    o = mms_start(p)
    if o < len(p) and p[o] == 0x61:
        e = ber(p, o)
        if not e:
            return None
        o += e[2]
        e = ber(p, o)
        if not e or p[o] != 0x30:
            return None
        o += e[2]
        while o < len(p) and p[o] != 0xA0:
            e = ber(p, o)
            if not e:
                return None
            o += e[2] + e[3]
        e = ber(p, o)
        if not e:
            return None
        o += e[2]
    return o if o < len(p) else None


def mms_fields(p, r):
    names = {(o, w): n for n, o, w in r['fields']}
    f = [(n, o, w) for n, o, w in r['fields'] if o < 7 and (n.startswith('tpkt.') or n.startswith('cotp.'))]
    o = 7
    if mms_start(p) == 11:
        f += [('ses.spdu_type', 7, 1), ('ses.length', 8, 1), ('ses.spdu_type', 9, 1), ('ses.length', 10, 1)]
        o = 11
    elif len(p) > 8 and p[7] in (0x0D, 0x0E):
        f += [('ses.spdu_type', 7, 1), ('ses.length', 8, 1)]
        return f

    def walk(o, end, depth):
        while o < end and len(f) < 80:
            e = ber(p, o)
            if not e:
                return
            num, cons, h, L = e
            tag_len = 1
            if p[o] & 0x1F == 0x1F:
                while o + tag_len < len(p) and p[o + tag_len] & 0x80:
                    tag_len += 1
                tag_len += 1
            f.append(('ber.tag', o, tag_len))
            f.append(('ber.length', o + tag_len, h - tag_len))
            v = o + h
            if cons and depth < 8:
                walk(v, min(v + L, end), depth + 1)
            elif L:
                f.append((names.get((v, L), 'value'), v, L))
            o = v + L
    walk(o, len(p), 0)
    return f


def mms_key(r, p):
    if len(p) > 8 and p[7] in (0x0D, 0x0E) and mms_start(p) == 7:
        return ('mms_session_connect_request', 'request') if p[7] == 0x0D else ('mms_session_accept_response', 'response')
    o = mms_pdu(p)
    if o is None:
        return None
    kind = MMS_PDU.get(p[o])
    if kind is None:
        return None
    if kind in ('confirmed_request', 'confirmed_response', 'confirmed_error'):
        e = ber(p, o)
        i = o + e[2] if e else len(p)
        e = ber(p, i)  # invokeID
        if not e:
            return None
        s = ber(p, i + e[2] + e[3])
        if not s:
            return None
        svc = MMS_SVC.get(s[0], f'service{s[0]}')
        suffix = {'confirmed_request': 'request', 'confirmed_response': 'response', 'confirmed_error': 'error'}[kind]
        return f'mms_{svc}_{suffix}', 'request' if suffix == 'request' else 'response'
    if kind == 'unconfirmed':
        e = ber(p, o)
        s = ber(p, o + e[2]) if e else None
        return f'mms_{MMS_UNCONF.get(s[0], "unconfirmed") if s else "unconfirmed"}', 'notification'
    return f'mms_{kind}', 'request' if kind.endswith('request') else 'response'


CONFIGS['mms'] = dict(
    protocol_name='MMS (ISO 9506) over ISO-on-TCP', version='ISO 9506 / IEC 61850-8-1', header_len=7, endian='big',
    strip=['tpkt.', 'cotp.', 'mms.', 'pres.', 'ses.', 'ber.'], fields_fn=mms_fields, header_overrides=TPKT_HEADER,
    roles={'spdu_type': 'function_code', 'tag': 'flags', 'length': 'length', 'invokeid': 'transaction_id',
           'presentation_context_identifier': 'constant', 'value': 'payload'},
    header_name='TPKT/COTP header', header_description=TPKT_COTP,
    key=mms_key, disc=False, relations=pairs,
    description='MMS over ISO-on-TCP (TCP/102): TPKT/COTP, session data-transfer SPDUs, presentation and the BER-encoded MMS PDU whose PDU type and service select the message type. BER tag, length and primitive value octets are separate fields where their offsets are fixed within a type.',
    offset_convention='TPKT/COTP fields use wire-absolute offsets 0..6; the other types are relative to offset 7 (session layer).')


# ---------------------------------------------------------------- held-out protocols (dol/heldout)
# Built after the method was frozen, for the overall score on protocols not used in development; written to
# truth_files/heldout/. Message types are the ones dol/heldout/prepare*.py already uses for the clustering scores.

C37_FT = {0: 'data', 1: 'header', 2: 'cfg1', 3: 'cfg2', 4: 'command', 5: 'cfg3'}


def c37_key(r, p):
    if len(p) < 14 or p[0] != 0xAA:
        return None
    ft = C37_FT.get((p[1] >> 4) & 7)
    if ft is None:
        return None
    return f'synphasor_{ft}', {'data': 'notification', 'command': 'request'}.get(ft, 'response')


CONFIGS['synphasor'] = dict(
    heldout=True, protocol_name='IEEE C37.118 synchrophasor', version='IEEE C37.118.2-2011', header_len=14, endian='big',
    strip=['synphasor.'], rename={'version': 'sync', 'frtype': 'sync', 'timeqal_lsocc': 'time_quality', 'timeqal_timequalindic': 'time_quality',
                                  'timeqal_lsdir': 'time_quality', 'timeqal_lspend': 'time_quality', 'fracsec_raw': 'fracsec', 'fracsec_ms': 'fracsec'},
    prefer=['sync', 'frsize', 'idcode', 'soc', 'fracsec', 'status', 'chk'],
    drop=[r'^synphasor\.(data\.(trigger_reason|data_modified|sorting|sync|pmu|time|config|error))', r'\.flag'],
    roles={'sync': 'function_code', 'frsize': 'length', 'idcode_stream_source': 'unit_id', 'soc': 'timestamp', 'fracsec': 'timestamp', 'time_quality': 'flags',
           'data_status': 'status', 'chk': 'checksum', 'command': 'function_code', 'cmd': 'function_code'},
    header_name='C37.118 common header', header_description='SYNC (frame type and version), frame size, ID code, SOC and FRACSEC.',
    key=c37_key, disc=False,
    relations=lambda ids: [('synphasor_command', t, 'A command frame requests a configuration frame.') for t in ('synphasor_cfg2', 'synphasor_cfg1', 'synphasor_cfg3')
                           if 'synphasor_command' in ids and t in ids][:1],
    description='IEEE C37.118 synchrophasor frames over TCP/UDP 4712: a 14-byte common header whose SYNC word carries the frame type (data, header, configuration 1/2/3, command), then the frame body and a CRC-CCITT.',
    offset_convention='Common header fields use wire-absolute offsets 0..13; frame types are relative to offset 14.')

ADS_CMD = {0: 'invalid', 1: 'read_device_info', 2: 'read', 3: 'write', 4: 'read_state', 5: 'write_control',
           6: 'add_notification', 7: 'delete_notification', 8: 'notification', 9: 'read_write'}


def ams_key(r, p):
    if len(p) < 38:
        return None
    cmd = int.from_bytes(p[22:24], 'little'); state = int.from_bytes(p[24:26], 'little')
    return (f'ams_{ADS_CMD.get(cmd, f"cmd{cmd}")}_{"response" if state & 1 else "request"}', 'response' if state & 1 else 'request')


CONFIGS['ams'] = dict(
    heldout=True, protocol_name='Beckhoff ADS/AMS over TCP', version='ADS (Beckhoff TwinCAT)', header_len=38, endian='little',
    strip=['ams.'], fields_fn=lambda p, r: r['fields'] + [('ams.tcp_reserved', 0, 2), ('ams.tcp_length', 2, 4)],
    drop=[r'^ams\.state_'],
    roles={'tcp_reserved': 'reserved', 'tcp_length': 'length', 'targetnetid': 'address', 'targetport': 'address', 'sendernetid': 'address',
           'senderport': 'address', 'cmdid': 'function_code', 'stateflags': 'flags', 'cbdata': 'length', 'errorcode': 'status',
           'invokeid': 'transaction_id', 'adsresult': 'status', 'ads_indexgroup': 'address', 'ads_indexoffset': 'address',
           'ads_cblength': 'length', 'ads_cbreadlength': 'length', 'ads_cbwritelength': 'length'},
    header_name='AMS/TCP and AMS header', header_description='AMS/TCP reserved and length, then target/sender AMS net id and port, command id, state flags, data length, error code and invoke id.',
    key=ams_key, disc=False, relations=pairs,
    description='Beckhoff ADS over AMS/TCP (TCP/48898): a 6-byte AMS/TCP header and a 32-byte AMS header whose command id and response flag select the message type, followed by the ADS command data.',
    offset_convention='AMS/TCP and AMS header fields use wire-absolute offsets 0..37; ADS types are relative to offset 38.')

DOIP_TYPE = {0x0000: 'nack', 0x0001: 'vehicle_id_request', 0x0004: 'vehicle_announcement', 0x0005: 'routing_activation_request',
             0x0006: 'routing_activation_response', 0x0007: 'alive_check_request', 0x0008: 'alive_check_response',
             0x8001: 'diagnostic_message', 0x8002: 'diagnostic_ack', 0x8003: 'diagnostic_nack'}
DOIP_ROLE = {'vehicle_id_request': 'request', 'routing_activation_request': 'request', 'alive_check_request': 'request',
             'diagnostic_ack': 'response', 'diagnostic_nack': 'response'}


def doip_key(r, p):
    if len(p) < 8:
        return None
    t = DOIP_TYPE.get(int.from_bytes(p[2:4], 'big'))
    if t is None:
        return None
    if t == 'diagnostic_message' and len(p) > 12:
        sid = p[12]
        if sid == 0x7F:
            return 'doip_uds_negative_response', 'response'
        reply = bool(sid & 0x40)
        return f'doip_uds_{sid & ~0x40 & 0xFF:02x}_{"response" if reply else "request"}', 'response' if reply else 'request'
    return f'doip_{t}', DOIP_ROLE.get(t, 'response')


CONFIGS['doip'] = dict(
    heldout=True, protocol_name='DoIP (ISO 13400-2) with UDS', version='ISO 13400-2:2019 / ISO 14229', header_len=8, endian='big',
    strip=['doip.', 'uds.'], prefer=['sid', 'type', 'length', 'source_address', 'target_address'],
    rename={'reply': 'sid'},
    roles={'version': 'constant', 'inverse': 'constant', 'type': 'function_code', 'length': 'length', 'source_address': 'address',
           'target_address': 'address', 'sid': 'function_code', 'diag_ack_code': 'status', 'diag_nack_code': 'status'},
    header_name='DoIP generic header', header_description='Protocol version, inverse version, payload type and payload length.',
    key=doip_key, disc=False,
    relations=pairs,
    description='Diagnostics over IP (TCP/UDP 13400): an 8-byte generic header whose payload type selects the message; diagnostic messages carry source and target addresses and a UDS PDU whose service id (with the reply bit) selects the type.',
    offset_convention='Generic header fields use wire-absolute offsets 0..7; payload types are relative to offset 8.')

LON_PDU = {0: 'tpdu', 1: 'spdu', 2: 'authpdu', 3: 'apdu'}
LON_TPDU = {0: 'ackd', 1: 'unackd_rpt', 2: 'ack', 4: 'reminder', 5: 'rem_msg'}
LON_SPDU = {0: 'request', 2: 'response', 4: 'reminder', 5: 'rem_msg'}


def cnip_key(r, p):
    if len(p) < 22:
        return None
    fmt = LON_PDU[(p[21] >> 4) & 3]
    sub = ''
    for name, table in (('lon.tpdu_type', LON_TPDU), ('lon.spdu_type', LON_SPDU)):
        o = at(r, name)
        if o is not None and o < len(p):
            sub = '_' + table.get((p[o] >> 4) & 7, str((p[o] >> 4) & 7))
    tid = f'cnip_{fmt}{sub}'
    return tid, 'response' if sub in ('_ack', '_response') else 'request'


CONFIGS['cnip'] = dict(
    heldout=True, protocol_name='CN/IP (EIA-852) with LonTalk', version='ANSI/EIA-852, ISO/IEC 14908-1', header_len=20, endian='big',
    strip=['cnip.', 'lon.'], prefer=['len', 'type', 'sessid', 'seqno', 'tstamp', 'ppdu', 'npdu', 'tpdu', 'spdu', 'selector'],
    rename={'ver': 'version', 'protocol': 'flags', 'pf': 'flags', 'sec': 'flags', 'alt_path': 'ppdu', 'prio': 'ppdu', 'delta_bl': 'ppdu',
            'addrfmt': 'npdu', 'pdufmt': 'npdu', 'domainlen': 'npdu', 'vers': 'npdu', 'trans_no': 'tpdu', 'auth': 'tpdu', 'tpdu_type': 'tpdu',
            'spdu_type': 'spdu', 'dir': 'nv_selector', 'selector': 'nv_selector', 'nv': 'nv_selector'},
    roles={'len': 'length', 'version': 'constant', 'type': 'function_code', 'exth': 'length', 'flags': 'flags', 'vendorcode': 'constant',
           'sessid': 'unit_id', 'seqno': 'sequence_number', 'tstamp': 'timestamp', 'ppdu': 'flags', 'npdu': 'function_code',
           'srcnet': 'address', 'srcnode': 'address', 'dstnet': 'address', 'dstnode': 'address', 'domain': 'address',
           'tpdu': 'function_code', 'spdu': 'function_code', 'nv_selector': 'address'},
    header_name='CN/IP header', header_description='Packet length, version, packet type, extended header size, protocol flags, vendor code, session id, sequence number and time stamp.',
    key=cnip_key, disc=False, relations=lambda ids: [],
    description='CN/IP (EIA-852) tunnelling of LonWorks over UDP 1628: a 20-byte CN/IP header and one LonTalk frame whose PDU format (TPDU, SPDU, AuthPDU, APDU) and TPDU/SPDU type select the message type.',
    offset_convention='CN/IP header fields use wire-absolute offsets 0..19; LonTalk types are relative to offset 20.')
