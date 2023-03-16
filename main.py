from slither import Slither
import sys
import argparse
import re



re_match_upgradeable = r"^.*Upgradeable$"



class Node :
  def __init__(self, nid, contract):
    """
      Graph node representing a smart contract

    """
    self.nid = nid
    self.contract = contract
    self.edge_in = set()
    self.edge_out = set()

  def add_edge_in(self, nid):
    """
      Add edge coming from external contract meaning that contract inherits
      from this contract 

    """
    self.edge_in.add(nid)

  def add_edge_out(self, nid):
    """
      Add edge going out to external contract meaning this contract inherits
      from that contract

    """
    self.edge_out.add(nid)

  def __str__(self):
    return "Node:{}(\"{}\")".format(self.nid, self.contract.name)

  def __repr__(self):
    return self.__str__()


class Checker:

  def __init__(self, proj_path, warn=False, comp=False):
    """
      Class implementing checks on the smart contracts

    """
    self.proj_path = proj_path
    self.slither = Slither(
      proj_path, 
      disable_solc_warnings=not warn,
      truffle_ignore_compile=not comp,
      embark_ignore_compile=not comp
    )
    self.__init_obj()

  def __init_obj(self):
    self.contracts = { x.name:Node(i,x) for i,x in enumerate(self.slither.contracts) }
    self.nodes_ht = [ x.name for x in self.slither.contracts ]
    self.__init_nodes()
    self.__init_upgradeable_sc()
    self.__init_abstract_sc()


  def __init_nodes(self):
    """
      Initialize graph 

    """
    for k,v in self.contracts.items() :

      for in_contract in v.contract.immediate_inheritance :
        in_name = in_contract.name

        if in_name not in self.contracts :
          self.contracts.update({in_name: Node(len(self.contracts), in_contract)})

        in_node = self.contracts[in_name]
        in_node.add_edge_in(v.nid)
        v.add_edge_out(in_node.nid)

  def __init_upgradeable_sc(self):
    """
      Save external upgradeable contracts

    """
    self.sc_upgradeable = set()
    for k,v in self.contracts.items() :
      if re.match(re_match_upgradeable, k) :
        if "openzeppelin/contracts-upgradeable" in v.contract.file_scope.filename.relative :
          self.sc_upgradeable.add(v.nid)

  def __init_abstract_sc(self):
    """
      Save abstract and interface contracts

    """
    self.sc_abstract = set()
    self.sc_interface = set()
    for k,v in self.contracts.items() :
      tmp_l = [x for x in v.contract.functions if not x.is_implemented]
      if tmp_l :
        if len(tmp_l) == len(v.contract.functions) :
          self.sc_interface.add(v.nid)
        else :
          self.sc_abstract.add(v.nid)


  def __visit(self, nid):
    if nid in self.path_now :
      return

    self.path_now.append(nid)

    if nid == self.destination_node :
      self.output_path.append(self.path_now[::])

    else :
      node = self.contracts[ self.nodes_ht[nid] ]
      for next_nid in node.edge_out :
        self.__visit(next_nid)

    self.path_now.pop(-1)
    return


  def visit(self, source_node, destination_node):
    """
      Returns list of paths if node_destination is reachable

    """ 

    if (source_node not in self.contracts) or (destination_node not in self.contracts) :
      print("[x] can't find '{}' and/or '{} contracts".format(source_node, destination_node))
      return []

    self.source_node = self.nodes_ht.index(source_node)
    self.destination_node = self.nodes_ht.index(destination_node)
    self.output_path = []
    self.path_now = []
    self.__visit(self.source_node)
    return self.output_path

  def print_path(self, paths):
    output = []
    space = ""
    for nid in paths:
      node = self.contracts[ self.nodes_ht[nid] ]
      output.append(space + "\-->" + str(node))
      space += "    "
    return "\n".join(output)

  def check_gap(self):
    """
      Test if gap variable is present for upgradeable contract
      ref: https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable

    """
    str_doc = "Missing gap on upgradeable contracts"
    rets = False

    if self.sc_upgradeable != set() :

      output = {}

      list_up = list(self.sc_upgradeable)
      i = 0

      while i < len(list_up) :
        nid = list_up[i]
        i += 1
        nid_name = self.nodes_ht[nid]
        node = self.contracts[nid_name]

        for inheriting_nid in node.edge_in :

          if inheriting_nid in self.sc_interface :
            continue

          contract = self.contracts[self.nodes_ht[inheriting_nid]].contract
          output_2 = []
          for var in contract.variables :
            if "__gap" in var.name and var.contract.name == contract.name :
              output_2.append(var)

          if output_2 == [] :
            if contract.name not in output :
              output[contract.name] = set()
            output[contract.name].add(nid_name)

            # update 'list_up'
            for nid_up in node.edge_in :
              if nid_up not in list_up :
                list_up.append(inheriting_nid)

      if output != {} :
        print("[!] {}:".format(str_doc))
        for k,v in output.items() :
          print(" - {} ({})".format(k, ", ".join(v)))
        rets = True

    return rets



if __name__ == "__main__" :
  parser = argparse.ArgumentParser(
    description="%s: Tool for doing security checks on smart contracts" % sys.argv[0]
  )
  parser.add_argument(
    "-w",
    default=False,
    action="store_true",
    help="Print compiler warnings (default False)"
  )
  parser.add_argument(
    "-c",
    default=False,
    action="store_true",
    help="Re/compile contracts"
  )
  parser.add_argument(
    "--path", 
    required=True, 
    help="Project's directory"
  )
  parser.add_argument(
    "--inheritance_check", 
    nargs='+',
    help="Print inheritance chains (expects two arguments)"
  )
  parser.add_argument(
    "--check_gap", 
    default=False, 
    action="store_true", 
    help="Check __gap missing on upgradeable contracts"
  )
  #
  args = parser.parse_args()
  path = args.path
  source_node = destination_node = None

  if args.inheritance_check :
    source_node, destination_node = args.inheritance_check
 
  ck = Checker(path, warn=args.w, comp=args.c)
 
  if source_node and destination_node :
    rets = ck.visit(source_node, destination_node)
    for chain in rets :
      print(ck.print_path(chain))
    print()

  if args.check_gap :
    ck.check_gap()

  print("[+] Done")


