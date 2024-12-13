import threading
import socket
import json
import time
import random

# Constants
NUM_NODES = 3
BASE_PORT = 5000
ELECTION_TIMEOUT_RANGE = (1.5, 3.0)
HEARTBEAT_INTERVAL = 0.5
CHECK_INTERVAL = 0.1
MAJORITY = (NUM_NODES // 2) + 1

FOLLOWER = "follower"
CANDIDATE = "candidate"
LEADER = "leader"

REQUEST_VOTE = "RequestVote"
REQUEST_VOTE_RESPONSE = "RequestVoteResponse"
APPEND_ENTRIES = "AppendEntries"
APPEND_ENTRIES_RESPONSE = "AppendEntriesResponse"


class Node(threading.Thread):
    def __init__(self, node_id, peers):
        super().__init__()
        self.node_id = node_id
        self.peers = peers
        self.role = FOLLOWER
        self.current_term = 0
        self.voted_for = None

        self.last_heartbeat = time.time()
        self.election_timeout = self.reset_election_timeout()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", BASE_PORT + self.node_id))
        self.sock.setblocking(False)

        self.votes_received = 0

    def reset_election_timeout(self):
        return time.time() + random.uniform(*ELECTION_TIMEOUT_RANGE)

    def log(self, message):
        # Helper function to prepend node info in logs.
        print(f"[Node {self.node_id} | Term {self.current_term} | Role {self.role}] {message}")

    def send_message(self, target_addr, message):
        data = json.dumps(message).encode('utf-8')
        try:
            self.sock.sendto(data, target_addr)
            self.log(f"Sent {message['type']} to {target_addr}")
        except Exception as e:
            self.log(f"Failed to send message to {target_addr}: {e}")

    def broadcast_message(self, message):
        for pid, addr in self.peers:
            self.send_message(addr, message)

    def start_election(self):
        self.role = CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = 1
        self.log(f"Election timeout! Becoming candidate for term {self.current_term}, voting for self.")
        self.election_timeout = self.reset_election_timeout()

        msg = {
            "type": REQUEST_VOTE,
            "term": self.current_term,
            "candidateId": self.node_id
        }
        self.log("Broadcasting RequestVote to all peers.")
        self.broadcast_message(msg)

    def send_heartbeats(self):
        msg = {
            "type": APPEND_ENTRIES,
            "term": self.current_term,
            "leaderId": self.node_id
        }
        self.log("Sending heartbeats to all followers.")
        self.broadcast_message(msg)

    def handle_request_vote(self, msg, addr):
        term = msg["term"]
        candidateId = msg["candidateId"]
        self.log(f"Received RequestVote from Node {candidateId} (term {term}).")

        if term < self.current_term:
            self.log("Candidate's term is lower; voting NO.")
            response = {
                "type": REQUEST_VOTE_RESPONSE,
                "term": self.current_term,
                "voteGranted": False
            }
            self.send_message(addr, response)
            return

        if term > self.current_term:
            self.log(f"Updating term from {self.current_term} to {term} and reverting to follower.")
            self.current_term = term
            self.role = FOLLOWER
            self.voted_for = None

        vote_granted = (self.voted_for is None or self.voted_for == candidateId)
        if vote_granted:
            self.voted_for = candidateId
            self.log(f"Voting for candidate {candidateId}.")
            self.election_timeout = self.reset_election_timeout()
        else:
            self.log(f"Already voted this term; cannot vote for candidate {candidateId}.")

        response = {
            "type": REQUEST_VOTE_RESPONSE,
            "term": self.current_term,
            "voteGranted": vote_granted
        }
        self.send_message(addr, response)

    def handle_request_vote_response(self, msg):
        term = msg["term"]
        voteGranted = msg["voteGranted"]
        self.log(f"Received RequestVoteResponse: voteGranted={voteGranted}, term={term}")

        if term > self.current_term:
            self.log("Received higher term in vote response, reverting to follower.")
            self.current_term = term
            self.role = FOLLOWER
            self.voted_for = None
            return

        if self.role == CANDIDATE and voteGranted:
            self.votes_received += 1
            self.log(f"Vote granted! Total votes now: {self.votes_received}")
            if self.votes_received >= MAJORITY:
                self.role = LEADER
                self.log(f"Became leader with majority votes in term {self.current_term}.")
                self.send_heartbeats()
                self.last_heartbeat = time.time()

